"""Repair the reported national EPSG:6933 failure without discarding progress.

Works when downloaded alone into tools/ of the original ZIP checkout. Never
submits a batch task. Server-side projection check and status checks precede edits.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid
import ee
from bdgee import PROJECT
from bdgee.batch import ACTIVE, ROOT, make_queue
from bdgee.core import initialize
from bdgee.state import exclusive_lock, write_json


def rewrite_projection(value):
    if isinstance(value,dict):
        if set(value)=={'__bdgee_expression__'}:
            graph=json.loads(value['__bdgee_expression__'])
            return {'__bdgee_expression__':json.dumps(rewrite_projection(graph))}
        return {k:rewrite_projection(v) for k,v in value.items()}
    if isinstance(value,list):return [rewrite_projection(v) for v in value]
    return 'EPSG:4326' if value=='EPSG:6933' else value


def prepare_repair(original,core_source,engine_hash,server_status):
    state=copy.deepcopy(original)
    if state.get('project')!=PROJECT or state.get('version')!=1:
        raise RuntimeError('Unexpected project/state version; refusing repair')
    settings=state['settings']
    if settings.get('mode')!='national':raise RuntimeError('This recovery is limited to the national queue')
    queue=make_queue('national',settings.get('themes'))
    if [j['key'] for j in state['jobs']]!=[j['key'] for j in queue]:
        raise RuntimeError('Saved queue does not match its settings')
    job=next((j for j in state['jobs'] if j['state']!='COMPLETED'),None)
    if not job or job['state']!='EXPORT_FAILED':raise RuntimeError('Current job is not EXPORT_FAILED; nothing changed')
    failed=next((t for t in job['tasks'] if t['state']!='VERIFIED'),None)
    if not failed or failed['state']!='FAILED' or server_status.get('id')!=failed['id']:
        raise RuntimeError('The saved failure does not match the server task')
    if server_status.get('state')!='FAILED' or 'CRS of a map projection could not be parsed' not in server_status.get('error_message',''):
        raise RuntimeError('Server does not confirm the expected projection failure')
    if 'EPSG:6933' not in json.dumps(failed['config']):
        raise RuntimeError('Failed task does not use the legacy projection; needs a separate diagnosis')
    for j in state['jobs']:
        for task in j['tasks']:
            if task['state']=='VERIFIED':continue
            if task is not failed and (task['state']!='NEW' or task.get('id')):
                raise RuntimeError('Another unverified submitted task exists; refusing automatic repair')
    # Only the known national default and native-population CRS argument change.
    corrected=core_source.replace("'EPSG:6933'", "'EPSG:4326'")
    corrected=corrected.replace("img.projection() if product.kind == 'count'", "img.projection().crs() if product.kind == 'count'")
    if 'EPSG:4326' not in corrected:raise RuntimeError('Unrecognized core.py projection configuration')
    for j in state['jobs']:
        for task in j['tasks']:
            if task['state']=='VERIFIED':continue
            task['config']=rewrite_projection(task['config'])
    history={k:copy.deepcopy(failed.get(k)) for k in ['id','request_id','state','status','config']}
    history['config']=copy.deepcopy(next(t for j in original['jobs'] for t in j['tasks'] if t['id']==failed['id'])['config'])
    failed.setdefault('attempt_history',[]).append(history)
    config=failed['config'];destination=config['fileExportOptions']['driveDestination']
    tag='_crsfix_'+uuid.uuid4().hex[:8]
    destination['filenamePrefix']=destination['filenamePrefix'][:95-len(tag)]+tag
    config['description']=destination['filenamePrefix']
    failed.update(id=None,request_id=str(uuid.uuid4()),state='NEW',files=[])
    failed.pop('status',None)
    job['state']='EXPORTING';job.pop('error',None)
    settings['engine_hash']=engine_hash
    state['fingerprint']=hashlib.sha256(json.dumps({'settings':settings,'queue':queue},sort_keys=True).encode()).hexdigest()
    state['phase']='STOPPED'
    state.setdefault('repairs',[]).append({'type':'projection_6933_to_4326','at':datetime.now(timezone.utc).isoformat(),'old_task':server_status['id']})
    return state,corrected


def repair(path):
    path=path.resolve()
    if Path(__file__).resolve().parents[1]!=ROOT.resolve():
        raise RuntimeError('Save this tool in tools/ of the same checkout as the installed bdgee package')
    with exclusive_lock(ROOT/'outputs/.sequential.lock'):
        initialize()
        state=json.loads(path.read_text(encoding='utf-8'))
        current=next((j for j in state['jobs'] if j['state']!='COMPLETED'),None)
        if not current or current['state']!='EXPORT_FAILED':raise RuntimeError('No current export failure to repair')
        task=next(t for t in current['tasks'] if t['state']!='VERIFIED')
        status=ee.data.getTaskStatus(task['id'])[0]
        if any(t.state in ACTIVE for t in ee.batch.Task.list()):raise RuntimeError('Other tasks are active; wait before repairing')
        # Verify actual server parsing/evaluation. The old offline tests could not.
        result=ee.Image.constant(1).reduceRegion(ee.Reducer.mean(),ee.Geometry.Rectangle([90,23,90.01,23.01]),scale=1000,crs='EPSG:4326',maxPixels=100).getInfo()
        if not result or result.get('constant')!=1:raise RuntimeError(f'EPSG:4326 preflight did not pass: {result}')
        core=ROOT/'bdgee/core.py';source=core.read_text(encoding='utf-8')
        # Calculate the fingerprint using the exact proposed on-disk core bytes.
        provisional=source.replace("'EPSG:6933'","'EPSG:4326'").replace("img.projection() if product.kind == 'count'","img.projection().crs() if product.kind == 'count'")
        code=b''.join(provisional.encode('utf-8') if p==core else p.read_bytes() for p in sorted((ROOT/'bdgee').glob('*.py')))+(ROOT/'tools/js_plan.cjs').read_bytes()
        digest=hashlib.sha256(code).hexdigest()
        fixed,corrected=prepare_repair(state,source,digest,status)
        backup=path.with_name(path.stem+'.before_projection_fix_'+uuid.uuid4().hex[:8]+'.json')
        write_json(backup,state)
        backup.with_suffix('.core.py.bak').write_bytes(core.read_bytes())
        # Binary UTF-8 write keeps the fingerprint identical on Windows (no CRLF conversion).
        core.write_bytes(corrected.encode('utf-8'))
        Path(importlib.util.cache_from_source(str(core))).unlink(missing_ok=True)
        write_json(path,fixed)
        print('Server projection check passed. State and core backups:',backup)
        print('Projection repaired; failed task reset with a fresh request/prefix. Completed exports preserved.')
        print('No export submitted. Resume your original climate test command now.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('state',type=Path)
    repair(p.parse_args().state)


if __name__=='__main__':main()
