"""Read actual task completion states for a saved national export plan."""
import argparse
import json
from pathlib import Path
import ee
from bdgee.core import initialize

p=argparse.ArgumentParser()
p.add_argument('plan',type=Path)
a=p.parse_args()
initialize()
rows=json.loads(a.plan.read_text())
ids=[r['id'] for r in rows if r.get('id')]
if not ids:raise SystemExit('This plan contains no submitted task IDs.')
statuses=ee.data.getTaskStatus(ids)
for status in statuses:
    print(status['id'],status['state'],status.get('error_message',''))
Path(a.plan.with_name('task_status.json')).write_text(json.dumps(statuses,indent=2))
if any(s['state'] in ('FAILED','CANCELLED') for s in statuses):raise SystemExit(1)
