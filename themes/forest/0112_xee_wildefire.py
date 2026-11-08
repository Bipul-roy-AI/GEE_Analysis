# Bangladesh adaptation: 0112_xee_wildefire
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'forest' / '0112_xee_wildefire'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""Untitled30.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-117: WildeFire Monitoring (Los Angles), using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap as gee
import xarray as xr
import xee
None
None
map = gee.Map(basemap='TERRAIN')
map
roi = BD_ROI
time_start = ee.Date('2025-01-01')
time_end = ee.Date('2025-02-01')
sr = ee.ImageCollection('NASA/VIIRS/002/VNP09GA').filterDate(time_start, time_end).select('I1', 'I2')

def ndvi(img):
    index = img.normalizedDifference(['I2', 'I1']).rename('ndvi')
    return index.copyProperties(img, img.propertyNames())
viirs_ndvi = sr.map(ndvi)
ds_ndvi = xr.open_dataset(viirs_ndvi, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds_ndvi
import matplotlib.pyplot as plt
ds_ndvi.ndvi.plot(x='lon', y='lat', col='time', col_wrap=5, robust=True, cmap='jet')
plt.savefig('ndvi_fire.png', dpi=360, bbox_inches='tight')
temp = ee.ImageCollection('NASA/VIIRS/002/VNP14A1').select('MaxFRP').filterDate(time_start, time_end)
ds_temp = xr.open_dataset(temp, engine='ee', crs='EPSG:4326', scale=0.005, geometry=BD_ROI)
ds_temp
ds_temp.MaxFRP.plot(x='lon', y='lat', cmap='Reds', col='time', col_wrap=5, robust=True)
lst = ee.ImageCollection('NASA/VIIRS/002/VNP21A1D').select('LST_1KM').filterDate(time_start, time_end)
ds_lst = xr.open_dataset(lst, engine='ee', crs='EPSG:4326', scale=0.005, geometry=BD_ROI)
ds_lst
ds_lst.LST_1KM.plot(x='lon', y='lat', cmap='hot_r', col='time', col_wrap=5, robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0112_xee_wildefire', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
