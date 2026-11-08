import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import ee
from ee.apitestcase import ApiTestCase
from bdgee.batch import Engine, pack, unpack
from bdgee.core import plan_product, validate_projection
from bdgee.workflows import products
from tools.repair_projection_failure import prepare_repair, rewrite_projection, repair

ERROR='Projection: The CRS of a map projection could not be parsed.'


def fixture_state():
    config={'expression':{'__bdgee_expression__':json.dumps({'crs':'EPSG:6933'})},'description':'original',
            'fileExportOptions':{'fileFormat':'GEO_TIFF','driveDestination':{'folder':'BD_GEE_climate','filenamePrefix':'original'}}}
    task={'id':'failed-id','request_id':'old-request','state':'FAILED','files':[],'config':config,'type':'EXPORT_IMAGE','status':{'error_message':ERROR}}
    pending=copy.deepcopy(task);pending.update(id=None,state='NEW',request_id='pending-request')
    return {'version':1,'project':'axial-paratext-491911-b6','settings':{'mode':'national','themes':['climate'],'engine_hash':'old'},
            'phase':'STOPPED','fingerprint':'old','jobs':[{'key':'national/climate','theme':'climate','state':'EXPORT_FAILED','tasks':[task,pending],'uploads':[]}]}


class RepairLogic(unittest.TestCase):
    def test_repairs_failed_and_pending_graphs_and_resume_fingerprint(self):
        state=fixture_state();original=copy.deepcopy(state)
        fixed,core=prepare_repair(state,"else 'EPSG:6933'",'new-hash',{'id':'failed-id','state':'FAILED','error_message':ERROR})
        self.assertEqual(state,original)
        task,pending=fixed['jobs'][0]['tasks']
        self.assertEqual(task['state'],'NEW');self.assertIsNone(task['id'])
        self.assertNotEqual(task['request_id'],'old-request')
        self.assertEqual(pending['request_id'],'pending-request')
        self.assertNotIn('EPSG:6933',json.dumps(task['config']))
        self.assertNotIn('EPSG:6933',json.dumps(pending['config']))
        self.assertIn('EPSG:6933',json.dumps(task['attempt_history'][0]['config']))
        self.assertEqual(core,"else 'EPSG:4326'")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json';p.write_text(json.dumps(fixed))
            resumed=Engine(p,fixed['settings'],[{'key':'national/climate','theme':'climate'}],None)
            self.assertEqual(resumed.state['jobs'][0]['state'],'EXPORTING')

    def test_preserves_verified_exports_exactly(self):
        state=fixture_state();done=copy.deepcopy(state['jobs'][0]['tasks'][0]);done.update(state='VERIFIED',id='completed-id',files=[{'id':'delivered-file'}])
        state['jobs'][0]['tasks'].insert(0,done)
        fixed,_=prepare_repair(state,"'EPSG:6933'",'new',{'id':'failed-id','state':'FAILED','error_message':ERROR})
        self.assertEqual(fixed['jobs'][0]['tasks'][0],done)

    def test_refuses_unrelated_failure_or_active_sibling(self):
        for status in [{'id':'failed-id','state':'RUNNING','error_message':ERROR}, {'id':'other','state':'FAILED','error_message':ERROR}, {'id':'failed-id','state':'FAILED','error_message':'Quota failure'}]:
            with self.assertRaises(RuntimeError):prepare_repair(fixture_state(),"'EPSG:6933'",'new',status)
        state=fixture_state();state['jobs'][0]['tasks'][1].update(state='RUNNING',id='other')
        with self.assertRaises(RuntimeError):prepare_repair(state,"'EPSG:6933'",'new',{'id':'failed-id','state':'FAILED','error_message':ERROR})


class ProjectionGraphs(ApiTestCase):
    def test_new_climate_graphs_and_roundtrip_use_4326(self):
        for t in plan_product(products('climate')[0],'climate','2024'):
            graph=unpack(pack(t.config))['expression'].serialize()
            self.assertIn('EPSG:4326',graph)
            self.assertNotIn('EPSG:6933',graph)

    def test_packed_legacy_graphs_are_actually_repaired(self):
        for t in plan_product(products('climate')[0],'climate','2024'):
            packed=pack(t.config)
            # Construct the old graph using the exact same serialization format.
            packed['expression']['__bdgee_expression__']=packed['expression']['__bdgee_expression__'].replace('EPSG:4326','EPSG:6933')
            graph=unpack(rewrite_projection(packed))['expression'].serialize()
            self.assertIn('EPSG:4326',graph)
            self.assertNotIn('EPSG:6933',graph)

    def test_projection_preflight_evaluates_and_requires_expected_value(self):
        with patch.object(ee.data,'computeValue',return_value={'constant':1}) as evaluate:
            validate_projection();self.assertTrue(evaluate.called)
        with patch.object(ee.data,'computeValue',return_value={}):
            with self.assertRaises(RuntimeError):validate_projection()
