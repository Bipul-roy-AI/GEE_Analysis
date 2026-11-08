"""Explicit authentication, reproducible boundaries, and lazy Drive export plans."""
from dataclasses import dataclass
import json
from pathlib import Path
import re
import ee
from . import PROJECT

BOUNDARY = 'FAO/GAUL/2015/level0'
ADMIN = 'FAO/GAUL/2015/level2'


def initialize(authenticate=False):
    if authenticate:
        ee.Authenticate(scopes=['https://www.googleapis.com/auth/earthengine',
                                'https://www.googleapis.com/auth/drive'])
    ee.Initialize(project=PROJECT)


def boundaries(admin_level=2):
    country = ee.FeatureCollection(BOUNDARY).filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'))
    units = ee.FeatureCollection(f'FAO/GAUL/2015/level{admin_level}').filter(
        ee.Filter.eq('ADM0_NAME', 'Bangladesh')) if admin_level else country
    return country, units


def safe_name(value):
    return re.sub(r'[^A-Za-z0-9_-]+', '_', str(value))[:95]


@dataclass
class Product:
    name: str
    image: object
    scale: int
    units: str
    kind: str = 'continuous'
    classes: tuple = ()


def plan_product(product, theme, period, admin_level=2):
    country, districts = boundaries(admin_level)
    roi = country.geometry()
    prefix = safe_name(f'BD_{theme}_{product.name}_{period}')
    folder = f'BD_GEE_{theme}'
    img = product.image.clip(roi)
    # count is the number of valid native/export-grid samples, not population.
    reducer = (ee.Reducer.mean().combine(ee.Reducer.stdDev(), sharedInputs=True)
               .combine(ee.Reducer.minMax(), sharedInputs=True)
               .combine(ee.Reducer.count(), sharedInputs=True))
    if product.kind == 'categorical':
        # Never average class labels. Each class gets a physically meaningful area.
        stats_img = ee.Image.cat([img.eq(c).multiply(ee.Image.pixelArea()).divide(1e6)
                                  .rename(f'class_{c}_km2') for c in product.classes])
        reducer = ee.Reducer.sum()
    elif product.kind == 'count':
        stats_img, reducer = img, ee.Reducer.sum()
    else:
        stats_img = img
    stats_crs = img.projection() if product.kind == 'count' else 'EPSG:6933'
    def annotate(feature):
        return feature.set({'product': product.name, 'period': period,
                            'units': 'km2 by class' if product.kind == 'categorical' else product.units,
                            'scale_m': product.scale, 'boundary': BOUNDARY,
                            'project': PROJECT}).setGeometry(None)
    table = stats_img.reduceRegions(collection=districts, reducer=reducer,
                                    scale=product.scale, crs=stats_crs, tileScale=4).map(annotate)
    national = stats_img.reduceRegions(collection=country, reducer=reducer,
                                      scale=product.scale, crs=stats_crs, tileScale=4).map(annotate)
    tasks = [ee.batch.Export.image.toDrive(
        image=img.toFloat(), description=prefix, folder=folder, fileNamePrefix=prefix,
        region=roi, scale=product.scale, crs=stats_crs, maxPixels=1e13,
        fileFormat='GeoTIFF', formatOptions={'cloudOptimized': True}),
        ee.batch.Export.table.toDrive(collection=table.merge(national), description=prefix+'_stats',
                                     folder=folder, fileNamePrefix=prefix+'_stats', fileFormat='CSV')]
    return tasks


def save_plan(tasks, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps([{'id': t.id, 'config': t.config, 'state': t.state}
                                     for t in tasks], default=str, indent=2))
