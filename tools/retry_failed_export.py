"""Explicitly retry ONLY the current failed export; never skip it or advance.

The server must confirm failure/cancellation. A fresh request/prefix prevents
partial old files from being accepted as the replacement export's outputs.
"""
import argparse
import json
from pathlib import Path
import uuid
import ee
from bdgee.batch import ACTIVE, BAD, ROOT, pack, unpack
from bdgee.core import initialize
from bdgee.state import exclusive_lock, write_json

p=argparse.ArgumentParser()
p.add_argument('state',type=Path)
a=p.parse_args()
with exclusive_lock(ROOT/'outputs/.sequential.lock'):
    initialize()
    state=json.loads(a.state.read_text())
    job=next((j for j in state['jobs'] if j['state']!='COMPLETED'),None)
    if not job or job['state']!='EXPORT_FAILED':raise SystemExit('Current job is not an export failure; no changes made.')
    task=next(t for t in job['tasks'] if t['state']!='VERIFIED')
    status=ee.data.getTaskStatus(task['id'])[0]
    if status['state'] not in BAD:raise SystemExit('Server does not confirm a failed/cancelled task; no changes made.')
    if any(t.state in ACTIVE for t in ee.batch.Task.list()):raise SystemExit('Active tasks exist; wait before retrying.')
    task.setdefault('attempt_history',[]).append({k:task.get(k) for k in ['id','request_id','state','status','config']})
    config=unpack(task['config'])
    destination=config['fileExportOptions']['driveDestination']
    tag='_retry_'+uuid.uuid4().hex[:8]
    destination['filenamePrefix']=destination['filenamePrefix'][:95-len(tag)]+tag
    config['description']=destination['filenamePrefix']
    task.update(id=None,request_id=str(uuid.uuid4()),state='NEW',files=[],config=pack(config))
    task.pop('status',None)
    job['state']='EXPORTING';job.pop('error',None)
    state['phase']='STOPPED'
    write_json(a.state,state)
    print('Failed task reset for retry. Resume the SAME runner command; no task was started by this tool.')
