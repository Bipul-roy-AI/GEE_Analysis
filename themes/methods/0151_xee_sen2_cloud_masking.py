# Bangladesh adaptation: 0151_xee_sen2_cloud_masking
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0151_xee_sen2_cloud_masking'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0071_sen2_cloud_mask.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-156: Sentienl-2 Cloud Masking using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xarray as xr
import xee
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi

def cloud_mask(img):
    qa = img.select('probability')
    cloud_mask = qa.lt(20)
    ms = img.select('B.*').multiply(0.0001)
    ndvi = ms.normalizedDifference(['B8', 'B4']).rename('ndvi')
    return ndvi.updateMask(cloud_mask).copyProperties(img, ['system:time_start'])
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').linkCollection(ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY'), 'probability').filterDate('2024', '2025').filterBounds(roi).map(cloud_mask)
sen2
ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.0003)
ds
ds = ds.sortby('time') * 1
ds_weekly = ds.resample(time='W').max('time')
ds_weekly.ndvi.plot(x='lon', y='lat', col='time', col_wrap=8, robust=True)
ds_rol = ds_weekly.rolling(time=15, min_periods=1, center=True).mean('time')
ds_rol.ndvi.plot(x='lon', y='lat', col='time', col_wrap=8, robust=True)
ds.sel(time=ds.time.dt.month == 7).ndvi.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0151_xee_sen2_cloud_masking', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
