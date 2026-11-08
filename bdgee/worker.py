"""Isolated tutorial planning workers. They cannot start EE exports."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import ee
from .batch import ROOT, pack, unpack
from .state import write_json


def plan_source(job,settings):
    out=ROOT/'outputs'/'batch_plans'/job['source']
    out.mkdir(parents=True,exist_ok=True)
    result=out/'plan.json'
    result.unlink(missing_ok=True)
    if job['language']=='python':
        command=[sys.executable,'-m','bdgee.worker',str(ROOT/job['adapted']),str(result)]
        environment=os.environ.copy();environment['MPLBACKEND']='Agg'
        import uuid
        environment['BDGEE_OUTPUT_DIR']=str(out/('attempt_'+uuid.uuid4().hex)/'local')
    else:
        from google.auth.transport.requests import Request
        credentials=ee.data.get_persistent_credentials()
        credentials.refresh(Request())
        environment=os.environ.copy()
        environment['BDGEE_ACCESS_TOKEN']=credentials.token
        command=['node',str(ROOT/'tools/js_plan.cjs'),str(ROOT/job['adapted']),str(result)]
    # Fully wait for this one process. Its plans never start exports themselves.
    with (out/'worker.log').open('w',encoding='utf-8') as log:
        completed=subprocess.run(command,cwd=ROOT,env=environment,stdout=log,stderr=subprocess.STDOUT)
    if completed.returncode or not result.exists():
        raise RuntimeError(f"Planning failed for {job['source']}; see {out/'worker.log'}. No next script will start.")
    payload=json.loads(result.read_text())
    tasks=[]
    for row in payload['tasks']:
        if row.get('raw_options'):
            # Bridge Code Editor-style options through the Python export builder.
            options=unpack(row['config'])
            method=ee.batch.Export.image.toDrive if row['type']=='EXPORT_IMAGE' else ee.batch.Export.table.toDrive
            tasks.append(method(**options))
        else:
            tasks.append(ee.batch.Task(None,row['type'],ee.batch.Task.State.UNSUBMITTED,unpack(row['config'])))
    files=[Path(p) for p in payload.get('local_files',[])]
    return tasks,files


def python_worker(source,result):
    from .core import initialize
    initialize()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.show=lambda *a,**kw:None
    ee.batch.Task.start=lambda *a,**kw:(_ for _ in ()).throw(RuntimeError('Worker must not submit an export; parent runner controls ordering'))
    # Credentials are inherited/refreshed by the SDK, never written into plans.
    try:
        namespace=runpy.run_path(str(source),run_name='__bdgee_tutorial__')
    finally:os.chdir(ROOT)
    tasks=namespace.get('bd_tasks',[])
    folder=namespace.get('_OUTPUT_DIR')
    if folder is None:raise RuntimeError('Tutorial has no local output directory')
    errors_path=Path(folder)/'export_errors.json'
    if errors_path.exists():
        errors=json.loads(errors_path.read_text())
        if errors:raise RuntimeError(f'Output export planning failed: {errors}; fix before continuing')
    files=[str(p.resolve()) for p in sorted(Path(folder).rglob('*')) if p.is_file()]
    if not tasks and not files:raise RuntimeError('No outputs found')
    write_json(result,{'tasks':[{'type':getattr(t.task_type,'value',t.task_type),'config':pack(t.config)} for t in tasks],'local_files':files})


if __name__=='__main__':python_worker(Path(sys.argv[1]),Path(sys.argv[2]))
