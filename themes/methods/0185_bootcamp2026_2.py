# Bangladesh adaptation: 0185_bootcamp2026_2
# Original author: Amirhossein Ahrari; see original attribution below and originals/.
from bdgee.core import initialize, boundaries
from bdgee.notebook import export_outputs, upload_local
initialize()  # Run `earthengine authenticate` first; project is configured in bdgee.
BD_COUNTRY, BD_DISTRICTS = boundaries()
BD_ROI = BD_COUNTRY.geometry()
BD_BBOX = [88.0, 20.5, 92.7, 26.7]  # search only, not analysis boundary
roi = geometry = border = iran = tehran = province = loc = point = BD_ROI
# Run from the repository root; all local outputs are isolated by source.
from pathlib import Path
import os
_REPO_ROOT = Path.cwd()
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0185_bootcamp2026_2'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""01_session1_intro_img_col_xarray.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session2: Cloud Masking and Band Math 

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
path_row_filter = ee.Filter.And(ee.Filter.eq('WRS_PATH', 162), ee.Filter.eq('WRS_ROW', 34))
cloud_cover = ee.Filter.And(ee.Filter.gt('CLOUD_COVER', 15), ee.Filter.lt('CLOUD_COVER', 30))
l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2025', '2026').filterBounds(roi).filter(path_row_filter).filter(cloud_cover).sort('system:time_start', False).first()

def cloud_mask(img):
    qa = img.select('QA_PIXEL')
    bit1 = qa.bitwiseAnd(1 << 1).neq(0)
    bit2 = qa.bitwiseAnd(1 << 2).neq(0)
    bit3 = qa.bitwiseAnd(1 << 3).neq(0)
    bit4 = qa.bitwiseAnd(1 << 4).neq(0)
    mask_layer = bit1.Or(bit2).Or(bit3).Or(bit4)
    sr = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    return sr.updateMask(mask_layer.Not())
l9_masked = cloud_mask(l9)
l9_ndvi = l9_masked.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
l9_ndvi2 = l9_masked.expression('(nir - red) / (nir + red)', {'nir': l9_masked.select('SR_B5'), 'red': l9_masked.select('SR_B4')}).rename('ndvi')
import xarray as xr
ds = xr.open_dataset(l9, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=100)
ds = ds.squeeze('time').drop_vars('time') * 1
ds.SR_B4.plot(x='X', y='Y', robust=True)
ds2 = xr.open_dataset(l9_masked, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=100)
ds2 = ds2.squeeze('time').drop_vars('time') * 1
ds2.SR_B4.plot(x='X', y='Y', robust=True)
nir = ds2['SR_B5']
red = ds2['SR_B4']
ds2['ndvi'] = (nir - red) / (nir + red)
ds2
ds2.ndvi.plot(x='X', y='Y', robust=True)
ds_ndvi = xr.open_dataset(l9_ndvi, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=100)
ds_ndvi = ds_ndvi.squeeze('time').drop_vars('time') * 1
ds_ndvi.ndvi.plot(x='X', y='Y', robust=True)
ds_ndvi2 = xr.open_dataset(l9_ndvi2, engine='ee', crs='EPSG:3857', scale=100, geometry=BD_ROI)
ds_ndvi2 = ds_ndvi2.squeeze('time').drop_vars('time') * 1
ds_ndvi2.ndvi.plot(x='X', y='Y', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0185_bootcamp2026_2', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
