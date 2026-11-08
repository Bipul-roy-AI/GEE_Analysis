"""Fail-closed sequential execution: script -> EE task -> verified Drive files.

There is deliberately no skip-failed or continue-on-error option. A stopped run
must resume with the same state/configuration before later work can execute.
"""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import uuid
import ee
from . import PROJECT
from .core import initialize, plan_product, boundaries
from .state import write_json, exclusive_lock
from .workflows import THEMES, products

ROOT=Path(__file__).resolve().parents[1]
ACTIVE={'READY','RUNNING','CANCEL_REQUESTED','PENDING','CANCELLING'}
BAD={'FAILED','CANCELLED'}


def pack(value):
    if isinstance(value,ee.ComputedObject):return {'__bdgee_expression__':ee.serializer.toJSON(value)}
    if isinstance(value,dict):return {k:pack(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [pack(v) for v in value]
    return value


def unpack(value):
    if isinstance(value,dict):
        if set(value)=={'__bdgee_expression__'}:return ee.deserializer.fromJSON(value['__bdgee_expression__'])
        return {k:unpack(v) for k,v in value.items()}
    if isinstance(value,list):return [unpack(v) for v in value]
    return value


def source_queue(themes=None):
    """Account for ALL sources, deferring supervised/empirical model families."""
    rows=json.loads((ROOT/'catalog.json').read_text())
    supervised=re.compile(r'RandomForest|XGBRegressor|GradientTreeBoost|libsvm|tensorflow|QuantileRegressor|LinearRegression|smileRandomForest|smileGradientTreeBoost|smileCart|\.train\s*\(\s*\{')
    for row in rows:
        text=(ROOT/row['adapted']).read_text(encoding='utf-8')
        row['deferred']=bool(supervised.search(text) or re.search(r'turbidity|chlorophyll|chl_water|cyanobacteria|cdom|tss',row['source'],re.I))
        row['defer_reason']='Supervised/empirical modelling deferred for local calibration and validation' if row['deferred'] else ''
    # Keep themes together, preserving numerical source order inside each theme.
    rows.sort(key=lambda r:(r['theme'],int(re.search(r'\d+',r['source'])[0])))
    return [r for r in rows if not themes or r['theme'] in themes]


def make_queue(mode, themes=None):
    if mode=='national':
        selected=themes or THEMES
        unknown=set(selected)-set(THEMES)
        if unknown:raise ValueError(f'Unknown national themes: {unknown}')
        return [{'key':'national/'+t,'theme':t} for t in selected]
    return [dict(r,key=r['source']) for r in source_queue(themes) if not r['deferred']]


def refresh_planning_source(path, settings, queue):
    """Accept an edited current script only when no export from it has started."""
    state=json.loads(Path(path).read_text())
    if state['settings']!=settings or len(state['jobs'])!=len(queue):
        raise RuntimeError('Runner/settings/queue changed; source-only refresh cannot accept that')
    current=next((j for j in state['jobs'] if j['state']!='COMPLETED'),None)
    if not current or current['state']!='PLAN_FAILED':raise RuntimeError('Only the current PLAN_FAILED source can be refreshed')
    if any(t.get('id') or t['state']!='NEW' for t in current['tasks']):raise RuntimeError('Exports already exist; refusing to change their source')
    for old,new in zip(state['jobs'],queue):
        for key,value in new.items():
            if old.get(key)!=value and not (old is current and key=='adapted_sha256'):
                raise RuntimeError('A different job or queue metadata changed; refusing refresh')
    replacement=next(q for q in queue if q['key']==current['key'])
    current.update(replacement)
    current['tasks']=[];current['uploads']=[]
    state['fingerprint']=hashlib.sha256(json.dumps({'settings':settings,'queue':queue},sort_keys=True).encode()).hexdigest()
    write_json(path,state)


class Engine:
    """Persistent state machine. Backend operations are injected for testing."""
    def __init__(self,path,settings,queue,backend,poll=30,sleep=time.sleep):
        self.path=Path(path);self.backend=backend;self.poll=poll;self.sleep=sleep
        digest=hashlib.sha256(json.dumps({'settings':settings,'queue':queue},sort_keys=True).encode()).hexdigest()
        if self.path.exists():
            self.state=json.loads(self.path.read_text())
            if self.state['fingerprint']!=digest:
                raise RuntimeError('Settings, source code or queue changed. Resume the unchanged run; use a separate state file for a deliberate new run.')
        else:
            self.state={'version':1,'project':PROJECT,'fingerprint':digest,'settings':settings,
                        'run_id':uuid.uuid4().hex[:12],'phase':'NEW',
                        'jobs':[dict(item,state='PENDING',tasks=[],uploads=[]) for item in queue]}
            self.save()

    def save(self):write_json(self.path,self.state)

    def run(self):
        for job_index,job in enumerate(self.state['jobs']):
            if job['state']=='COMPLETED':continue
            print(f"[{job_index+1}/{len(self.state['jobs'])}] {job['key']} ({job['state']})",flush=True)
            try:
                if job['state'] in ('PENDING','PLANNING','PLAN_FAILED'):
                    self.backend.assert_idle()
                    job['state']='PLANNING';job['tasks']=[];job['uploads']=[];self.save()
                    # A planner is forbidden from submitting exports. No following
                    # source is launched until this job's final Drive gate passes.
                    planned,local_files=self.backend.plan(job)
                    if not planned and not local_files:raise RuntimeError('No exportable outputs found; refusing to call this script completed')
                    for i,task in enumerate(planned):
                        config=task.config.copy()
                        options=config.get('fileExportOptions',{})
                        dest=options.get('driveDestination')
                        if dest is None:raise RuntimeError('Only Google Drive exports are accepted by the batch runner')
                        tag=f"_{self.state['run_id']}_{job_index}_{i}"
                        prefix=re.sub(r'[^A-Za-z0-9_-]','_',str(dest.get('filenamePrefix') or config['description']))[:95-len(tag)]+tag
                        options=dict(options,driveDestination={'folder':'BD_GEE_'+job['theme'],'filenamePrefix':prefix})
                        config.update(description=prefix,fileExportOptions=options)
                        job['tasks'].append({'type':getattr(task.task_type,'value',task.task_type),'config':pack(config),
                                             'request_id':str(uuid.uuid4()),'id':None,'state':'NEW','files':[]})
                    job['uploads']=self.backend.prepare_uploads(local_files,job,self.state['run_id'])
                    job['state']='EXPORTING';self.save()
                if job['state']=='EXPORT_FAILED':
                    raise RuntimeError('A previous export failed/cancelled. Inspect the report; use the documented retry procedure for that task before resuming.')
                for task in job['tasks']:
                    if task['state']=='VERIFIED':continue
                    if task['state']=='NEW':
                        self.backend.assert_idle()
                        task['state']='SUBMITTING';self.save()
                    if task['state']=='SUBMITTING':
                        # Stable request ID is persisted before the call. Retrying
                        # the same request is idempotent even if the response was lost.
                        self.backend.assert_idle(allow_request=task['request_id'])
                        task['id']=self.backend.submit(task)
                        task['state']='READY';self.save()
                    while task['state']!='COMPLETED':
                        status=self.backend.status(task['id'])
                        state=status.get('state','UNKNOWN')
                        task['state']=state;task['status']=status;self.save()
                        if state in BAD:
                            job['state']='EXPORT_FAILED';self.save()
                            raise RuntimeError(f"{task['id']}: {state}: {status.get('error_message','')}")
                        if state=='COMPLETED':break
                        if state not in ACTIVE:raise RuntimeError(f'Unknown task status {state}; no further work started')
                        print(f"  {task['id']}: {state}",flush=True)
                        self.sleep(self.poll)
                    # COMPLETED is necessary but not enough: verify nonempty
                    # destination files via Drive API before the next task starts.
                    task['files']=self.backend.verify_export(task)
                    if not task['files']:raise RuntimeError('Drive verification returned no output files')
                    task['state']='VERIFIED';self.save()
                    print(f"  verified {len(task['files'])} Drive file(s)",flush=True)
                for upload in job['uploads']:
                    if upload['state']=='VERIFIED':continue
                    self.backend.upload_and_verify(upload)
                    upload['state']='VERIFIED';self.save()
                job['state']='COMPLETED';job['completed_at']=datetime.now(timezone.utc).isoformat()
                job.pop('error',None);self.save()
            except BaseException as exc:
                job['error']=str(exc)
                if job['state']=='PLANNING':job['state']='PLAN_FAILED'
                self.state['phase']='STOPPED';self.save()
                raise
        self.state['phase']='COMPLETED';self.save()
        print('All selected scripts and exports completed and verified.',flush=True)


class LiveBackend:
    def __init__(self,settings,poll=30):
        from googleapiclient.discovery import build
        self.settings=settings;self.poll=poll
        self.credentials=ee.data.get_persistent_credentials()
        self.drive=build('drive','v3',credentials=self.credentials,cache_discovery=False)
        # Required upfront; never start EE tasks then discover that Drive is inaccessible.
        self.drive.files().list(pageSize=1,fields='files(id)').execute()

    def assert_idle(self,allow_request=None):
        active=[t for t in ee.batch.Task.list() if t.state in ACTIVE]
        if active:
            # Never guess a submitted task's ID after an ambiguous response.
            # The saved request ID can safely be replayed, but unrelated active
            # jobs must not be overlapped.
            if allow_request:
                raise RuntimeError('An EE task is active after an interrupted submission. Reconcile its ID with the saved SUBMITTING task before resuming (see SEQUENTIAL.md).')
            raise RuntimeError('Earth Engine already has active tasks. Wait for completion/cancellation before this batch starts.')

    def plan(self,job):
        if job['key'].startswith('national/'):
            country,units=boundaries(self.settings['admin_level'])
            if country.size().getInfo()!=1 or units.size().getInfo()==0:raise RuntimeError('Boundary preflight failed')
            tasks=[]
            for product in products(job['theme'],self.settings['start'],self.settings['end']):
                if not product.image.bandNames().getInfo():raise RuntimeError(f'Empty product: {product.name}')
                tasks.extend(plan_product(product,job['theme'],self.settings['start']+'_'+self.settings['end'],self.settings['admin_level']))
            return tasks,[]
        from .worker import plan_source
        return plan_source(job,self.settings)

    def submit(self,record):
        task=ee.batch.Task(None,record['type'],ee.batch.Task.State.UNSUBMITTED,unpack(record['config']))
        task._request_id=record['request_id']
        task.start()
        return task.id

    def status(self,task_id):return ee.data.getTaskStatus(task_id)[0]

    def folder(self,name):
        result=self.drive.files().list(q="trashed = false and mimeType = 'application/vnd.google-apps.folder' and name = '"+name+"'",fields='files(id,name)',pageSize=100).execute()['files']
        if len(result)>1:raise RuntimeError(f'Duplicate Drive folders named {name}; resolve duplicates first')
        return result[0]['id'] if result else None

    def verify_export(self,task):
        options=unpack(task['config'])['fileExportOptions'];dest=options['driveDestination']
        # Allow eventual visibility, but never advance when this gate times out.
        deadline=time.monotonic()+600
        suffix={'GEO_TIFF':'.tif','CSV':'.csv','GEO_JSON':'.geojson','SHP':'.zip','KML':'.kml','KMZ':'.kmz','TF_RECORD_TABLE':'.tfrecord.gz'}.get(options['fileFormat'])
        if suffix is None:raise RuntimeError(f"Unsupported Drive verification format: {options['fileFormat']}")
        prefix=dest['filenamePrefix']
        while True:
            parent=self.folder(dest['folder']);files=[]
            if parent:
                token=None
                while True:
                    result=self.drive.files().list(q=f"trashed = false and '{parent}' in parents and name contains '{prefix}'",fields='nextPageToken,files(id,name,size,mimeType)',pageToken=token,pageSize=1000).execute()
                    files.extend(f for f in result.get('files',[]) if (f['name']==prefix+suffix or (f['name'].startswith(prefix+'-') and f['name'].endswith(suffix))))
                    token=result.get('nextPageToken')
                    if not token:break
            if files and all(int(f.get('size',0))>0 for f in files):return files
            if time.monotonic()>=deadline:raise RuntimeError(f'EE completed but Drive files are not visible/nonempty for {prefix}; resume later, no next task started')
            time.sleep(self.poll)

    def prepare_uploads(self,files,job,run_id):
        out=[]
        for index,file in enumerate(files):
            path=Path(file).resolve()
            out.append({'path':str(path),'size':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'folder':'BD_GEE_'+job['theme'],'name':job['key']+'_'+run_id+'_'+str(index)+'_'+path.name,
                        'id':self.drive.files().generateIds(count=1,space='drive').execute()['ids'][0],'state':'NEW'})
        return out

    def upload_and_verify(self,record):
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        path=Path(record['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise RuntimeError('Local output changed since planning; refusing to upload it as the saved result')
        try:metadata=self.drive.files().get(fileId=record['id'],fields='id,name,size,md5Checksum').execute()
        except HttpError as exc:
            if exc.resp.status!=404:raise
            parent=self.folder(record['folder'])
            if parent is None:
                parent=self.drive.files().create(body={'name':record['folder'],'mimeType':'application/vnd.google-apps.folder'},fields='id').execute()['id']
            metadata=self.drive.files().create(body={'id':record['id'],'name':record['name'],'parents':[parent]},media_body=MediaFileUpload(str(path),resumable=True),fields='id,name,size,md5Checksum').execute()
        if int(metadata.get('size',-1))!=record['size'] or metadata.get('md5Checksum')!=hashlib.md5(path.read_bytes()).hexdigest():
            raise RuntimeError('Drive upload size/checksum verification failed')
        record['file']=metadata


def main(argv=None):
    p=argparse.ArgumentParser(description='Run one analysis/export at a time; verify Drive delivery before advancing')
    p.add_argument('--mode',choices=['national','tutorials'],default='national')
    p.add_argument('--themes',nargs='+')
    p.add_argument('--start',default='2024-01-01');p.add_argument('--end',default='2025-01-01')
    p.add_argument('--admin-level',type=int,choices=[0,1,2],default=2)
    p.add_argument('--poll-seconds',type=int,default=30)
    p.add_argument('--state',type=Path)
    p.add_argument('--authenticate',action='store_true')
    p.add_argument('--refresh-planning-source',action='store_true',help='Accept edits to the current PLAN_FAILED tutorial only, before any exports exist')
    p.add_argument('--run',action='store_true',help='Without this flag, write the queue report only (no login or exports)')
    a=p.parse_args(argv)
    if a.poll_seconds<5:p.error('Polling must be >=5 seconds')
    if date.fromisoformat(a.start)>=date.fromisoformat(a.end):p.error('start must precede end')
    queue=make_queue(a.mode,a.themes)
    if not queue:p.error('No jobs matched the requested themes')
    # Bind resume to both source and runner versions; changed logic needs review.
    engine_hash=hashlib.sha256(b''.join(path.read_bytes() for path in sorted((ROOT/'bdgee').glob('*.py')))+ (ROOT/'tools/js_plan.cjs').read_bytes()).hexdigest()
    settings={'mode':a.mode,'themes':a.themes,'start':a.start,'end':a.end,'admin_level':a.admin_level,'engine_hash':engine_hash}
    if a.mode=='tutorials':
        for job in queue:job['adapted_sha256']=hashlib.sha256((ROOT/job['adapted']).read_bytes()).hexdigest()
    report={'project':PROJECT,'settings':settings,'queue':queue,'deferred': [r for r in source_queue(a.themes) if r['deferred']] if a.mode=='tutorials' else []}
    report_path=ROOT/'outputs'/f'{a.mode}_queue.json';write_json(report_path,report)
    print(f'{len(queue)} jobs selected; {len(report["deferred"])} deferred; report {report_path}')
    if not a.run:return
    with exclusive_lock(ROOT/'outputs/.sequential.lock'):
        initialize(a.authenticate)
        backend=LiveBackend(settings,a.poll_seconds)
        state_path=a.state or ROOT/'outputs'/f'{a.mode}_state.json'
        if a.refresh_planning_source:refresh_planning_source(state_path,settings,queue)
        engine=Engine(state_path,settings,queue,backend,a.poll_seconds)
        engine.run()


if __name__=='__main__':main()
