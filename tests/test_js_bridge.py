"""Exercise actual JS SDK -> Python SDK graph transport, without network access."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest
import ee
from ee.apitestcase import ApiTestCase, GetAlgorithms
from bdgee.batch import ROOT, pack, unpack


class Bridge(ApiTestCase):
    def test_computed_config_roundtrip(self):
        original={'image':ee.Image.constant(2).add(3),'nested':[ee.Number(2)]}
        result=unpack(json.loads(json.dumps(pack(original))))
        self.assertEqual(original['image'].serialize(),result['image'].serialize())
        self.assertEqual(original['nested'][0].serialize(),ee.Number(result['nested'][0]).serialize())

    def test_two_actual_javascript_tutorials_plan_through_both_sdks(self):
        if not shutil.which('node') or not (ROOT/'node_modules/@google/earthengine').exists():
            pytest.skip('Install npm dependencies to run the JS bridge test')
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            algorithms=root/'algorithms.json';algorithms.write_text(json.dumps(GetAlgorithms()))
            environment=dict(os.environ,BDGEE_OFFLINE_ALGORITHMS=str(algorithms))
            for source in ['themes/water/00001_lake_area_estimation.js','themes/water/00002_lake_area_monitoring.js']:
                result=root/'plan.json'
                run=subprocess.run(['node',str(ROOT/'tools/js_plan.cjs'),str(ROOT/source),str(result)],env=environment,capture_output=True,text=True,timeout=60)
                self.assertEqual(run.returncode,0,run.stderr)
                rows=json.loads(result.read_text())['tasks']
                self.assertTrue(rows)
                for row in rows:
                    options=unpack(row['config'])
                    fn=ee.batch.Export.image.toDrive if row['type']=='EXPORT_IMAGE' else ee.batch.Export.table.toDrive
                    task=fn(**options)
                    self.assertIsNone(task.id)
                    self.assertIn('expression',task.config)
                    self.assertTrue(task.config['expression'].serialize())

    def test_restored_export_task_types_and_stable_request_ids(self):
        from unittest.mock import patch
        from bdgee.batch import LiveBackend
        b=LiveBackend.__new__(LiveBackend)
        for task in [ee.batch.Export.image.toDrive(ee.Image.constant(1),description='test'),
                     ee.batch.Export.table.toDrive(ee.FeatureCollection([]),description='test')]:
            record={'type':task.task_type.value,'config':pack(task.config),'request_id':'stable-request'}
            endpoint='exportImage' if task.task_type==ee.batch.Task.Type.EXPORT_IMAGE else 'exportTable'
            with patch.object(ee.data,endpoint,return_value={'name':'projects/test/operations/operation-id'}) as call:
                self.assertEqual(b.submit(record),'operation-id')
                self.assertEqual(call.call_args.args[0],'stable-request')
