# Bangladesh adaptation: 0184_bootcamp2026_1
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0184_bootcamp2026_1'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""01_session1_intro_img_col_xarray.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session1: Image Collection vs. Xarray

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
l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2025', '2026').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 10)).select('SR_B.*').filter(ee.Filter.eq('WRS_PATH', 166)).filter(ee.Filter.eq('WRS_ROW', 34)).first()
l9
import xarray as xr
ds = xr.open_dataset(l9, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=30)
ds = ds.squeeze('time').drop_vars('time') * 1
ds
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2025', '2026').filterBounds(roi).select('B[2-4]', 'B8').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).first().multiply(1)
sen2
test = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2025', '2026').filterBounds(roi).select('B[2-4]', 'B8').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).first().multiply(1)
test
ds2 = xr.open_dataset(sen2, engine='ee', crs='EPSG:3857', scale=10, geometry=BD_ROI)
ds_test = xr.open_dataset(test, engine='ee', crs='EPSG:3857', scale=10, geometry=BD_ROI)
ds_test = ds_test.squeeze('time').drop_vars('time') * 1
ds_test * 0.0001

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0184_bootcamp2026_1', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
