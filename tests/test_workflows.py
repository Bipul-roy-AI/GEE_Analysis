"""Offline graph tests use the EE SDK's bundled API signatures, never fake pixels.
These detect graph/type/export errors but do not prove asset availability or results.
"""
import json
from pathlib import Path
import ast
import unittest
import ee
from ee.apitestcase import ApiTestCase
from bdgee.core import Product, plan_product, safe_name
from bdgee.workflows import THEMES, products


class WorkflowGraphs(ApiTestCase):
    def test_every_national_workflow_serializes(self):
        for theme in THEMES:
            with self.subTest(theme=theme):
                result=products(theme)
                self.assertTrue(result)
                for product in result:
                    self.assertTrue(json.loads(product.image.serialize()))
                    tasks=plan_product(product,theme,'2024')
                    self.assertEqual(len(tasks),2)
                    self.assertEqual(tasks[0].config['fileExportOptions']['driveDestination']['folder'],'BD_GEE_'+theme)
                    self.assertEqual(tasks[1].config['fileExportOptions']['fileFormat'],'CSV')
                    self.assertIsNone(tasks[0].id)

    def test_categorical_statistics_use_area_not_label_mean(self):
        tasks=plan_product(Product('classes',ee.Image.constant(1),30,'class','categorical',(0,1,2)),'landcover','2024')
        graph=tasks[1].config['expression'].serialize()
        self.assertIn('Image.pixelArea',graph)
        self.assertIn('Reducer.sum',graph)
        self.assertNotIn('Reducer.mean',graph)

    def test_population_summed_not_averaged(self):
        task=plan_product(Product('pop',ee.Image.constant(1),100,'people','count'),'population','2020')[1]
        self.assertIn('Reducer.sum',task.config['expression'].serialize())
        self.assertNotIn('Reducer.mean',task.config['expression'].serialize())


class Inventory(unittest.TestCase):
    def test_archive_coverage_and_hashes(self):
        import hashlib
        root=Path(__file__).resolve().parents[1]
        records=json.loads((root/'catalog.json').read_text())
        self.assertEqual(len(records),245)
        for rec in records:
            self.assertEqual(rec['status'],'adapted_unverified',rec['source'])
            self.assertEqual(hashlib.sha256((root/'originals'/rec['source']).read_bytes()).hexdigest(),rec['sha256'])
            file=root/rec['adapted']
            self.assertTrue(file.exists())
            if file.suffix=='.py':ast.parse(file.read_text())
            self.assertNotIn("project='ee-amirhosseinahrari'", file.read_text())

    def test_safe_task_names(self):
        self.assertEqual(safe_name('a / b'),'a_b')
        self.assertLessEqual(len(safe_name('x'*200)),95)
