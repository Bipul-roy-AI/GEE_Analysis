"""Ordering, durable resume and failure gates with a deterministic fake backend."""
import json
from types import SimpleNamespace
import pytest
from bdgee.batch import Engine, make_queue, source_queue
from bdgee.state import exclusive_lock


class Backend:
    def __init__(self):self.events=[];self.states={};self.verify_fail=False;self.fail_task=False;self.poll_fail=False
    def assert_idle(self,**kwargs):self.events.append('idle')
    def plan(self,job):
        self.events.append('plan:'+job['key'])
        task=lambda:SimpleNamespace(task_type='EXPORT_IMAGE',config={'description':'test','fileExportOptions':{'fileFormat':'GEO_TIFF','driveDestination':{'folder':'BD_GEE_test','filenamePrefix':'test'}}})
        return [task(),task()],[]
    def prepare_uploads(self,*args):return []
    def submit(self,record):
        task_id=str(len(self.states)+1);self.states[task_id]=0;self.events.append('submit:'+task_id);return task_id
    def status(self,task_id):
        self.events.append('status:'+task_id)
        if self.poll_fail:raise OSError('network interrupted')
        self.states[task_id]+=1
        return {'state':'FAILED' if self.fail_task else ('RUNNING' if self.states[task_id]==1 else 'COMPLETED')}
    def verify_export(self,record):
        self.events.append('verify:'+record['id'])
        if self.verify_fail:raise RuntimeError('Drive output missing')
        return [{'id':'file-'+record['id'],'size':'123'}]


def engine(tmp_path,backend):return Engine(tmp_path/'state.json',{'project':'test'},[{'key':'A','theme':'test'},{'key':'B','theme':'test'}],backend,poll=0,sleep=lambda _:None)


def test_strict_order_across_tasks_and_sources(tmp_path):
    b=Backend();r=engine(tmp_path,b);r.run()
    for n in range(1,4):assert b.events.index('verify:'+str(n))<b.events.index('submit:'+str(n+1))
    assert b.events.index('verify:2')<b.events.index('plan:B')
    assert r.state['phase']=='COMPLETED'


def test_drive_failure_blocks_next_task_and_resume_does_not_resubmit(tmp_path):
    b=Backend();b.verify_fail=True
    with pytest.raises(RuntimeError,match='Drive'):engine(tmp_path,b).run()
    assert b.events.count('submit:1')==1 and 'submit:2' not in b.events and 'plan:B' not in b.events
    b.verify_fail=False
    engine(tmp_path,b).run()
    assert b.events.count('submit:1')==1
    assert b.events.count('plan:A')==1


def test_failed_export_stops_and_stays_stopped_on_resume(tmp_path):
    b=Backend();b.fail_task=True
    with pytest.raises(RuntimeError):engine(tmp_path,b).run()
    with pytest.raises(RuntimeError,match='previous export'):engine(tmp_path,b).run()
    assert 'plan:B' not in b.events and 'submit:2' not in b.events


def test_status_network_failure_resumes_existing_task(tmp_path):
    b=Backend();b.poll_fail=True
    with pytest.raises(OSError):engine(tmp_path,b).run()
    b.poll_fail=False
    engine(tmp_path,b).run()
    assert b.events.count('submit:1')==1


def test_unknown_status_cannot_advance(tmp_path):
    b=Backend();b.status=lambda _: {'state':'UNKNOWN'}
    with pytest.raises(RuntimeError,match='Unknown task'):engine(tmp_path,b).run()
    assert 'submit:2' not in b.events


def test_changed_configuration_refused(tmp_path):
    b=Backend();engine(tmp_path,b)
    with pytest.raises(RuntimeError,match='changed'):Engine(tmp_path/'state.json',{'different':1},[],b)


def test_already_completed_run_never_repeats(tmp_path):
    b=Backend();engine(tmp_path,b).run();events=b.events.copy();engine(tmp_path,b).run()
    assert b.events==events


def test_single_runner_lock(tmp_path):
    with exclusive_lock(tmp_path/'lock'):
        with pytest.raises(RuntimeError,match='Another batch'):
            with exclusive_lock(tmp_path/'lock'):pass


def test_full_inventory_accounted_for_with_explicit_deferrals():
    rows=source_queue();queue=make_queue('tutorials')
    assert len(rows)==245
    assert len(queue)+sum(r['deferred'] for r in rows)==245
    assert len(make_queue('national'))==16
    assert any(r['source']=='0174_biomass_embedding' and r['deferred'] for r in rows)
    assert any(r['source']=='0159_xee_sen2_turbidity' and r['deferred'] for r in rows)


def test_local_upload_failure_blocks_next_source(tmp_path):
    b=Backend()
    b.prepare_uploads=lambda *args:[{'state':'NEW'}]
    def upload(_):
        b.events.append('upload')
        raise RuntimeError('upload checksum mismatch')
    b.upload_and_verify=upload
    with pytest.raises(RuntimeError,match='checksum'):engine(tmp_path,b).run()
    assert 'plan:B' not in b.events
    b.upload_and_verify=lambda _:b.events.append('upload:verified')
    engine(tmp_path,b).run()
    assert b.events.count('submit:1')==1
    assert b.events.index('upload:verified')<b.events.index('plan:B')


def test_partial_planner_failure_does_not_duplicate_tasks(tmp_path):
    b=Backend()
    def fail(*args):raise RuntimeError('Drive ids unavailable')
    b.prepare_uploads=fail
    with pytest.raises(RuntimeError):engine(tmp_path,b).run()
    b.prepare_uploads=lambda *args:[]
    r=engine(tmp_path,b);r.run()
    assert len(r.state['jobs'][0]['tasks'])==2
    assert len(b.states)==4


def test_refresh_only_current_unsubmitted_failed_source(tmp_path):
    from bdgee.batch import refresh_planning_source
    b=Backend();queue=[{'key':'A','theme':'test','adapted_sha256':'old'}]
    settings={'project':'test'}
    r=Engine(tmp_path/'state.json',settings,queue,b)
    r.state['jobs'][0]['state']='PLAN_FAILED';r.save()
    new=[dict(queue[0],adapted_sha256='new')]
    refresh_planning_source(tmp_path/'state.json',settings,new)
    updated=Engine(tmp_path/'state.json',settings,new,b)
    assert updated.state['jobs'][0]['adapted_sha256']=='new'
    updated.state['jobs'][0]['state']='EXPORTING';updated.save()
    with pytest.raises(RuntimeError,match='PLAN_FAILED'):refresh_planning_source(tmp_path/'state.json',settings,new)
