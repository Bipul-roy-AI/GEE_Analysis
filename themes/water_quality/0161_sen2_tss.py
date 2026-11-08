# Bangladesh adaptation: 0161_sen2_tss
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'water_quality' / '0161_sen2_tss'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0084_total_suspended_solid.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-166:  Sentinel-2 Total Suspended Solid for Water Body

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
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').linkCollection(ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY'), 'probability').filterBounds(roi).filterDate('2024', '2025')

def index(img):
    cloud_band = img.select('probability')
    cloud_free = cloud_band.lt(20)
    ms_bands = img.select('B.*').multiply(0.0001)
    ndwi = ms_bands.normalizedDifference(['B3', 'B8']).rename('ndwi')
    water_body = ndwi.gt(0.1)
    tss = ms_bands.expression('b7 * (b5/b2)', {'b2': ms_bands.select('B2'), 'b5': ms_bands.select('B5'), 'b7': ms_bands.select('B7')}).rename('tss')
    return tss.updateMask(cloud_free).updateMask(water_body).copyProperties(img, ['system:time_start'])
sen2_index = sen2.map(index)
sen2_index
import xarray as xr
ds = xr.open_dataset(sen2_index, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds_monthly = ds.resample(time='M').median('time')
import matplotlib.pyplot as plt
ds_monthly.tss.plot.contourf(x='lon', y='lat', col='time', col_wrap=6, robust=True, cmap='turbo', levels=10)
plt.savefig('tss_map.png', dpi=360, bbox_inches='tight')
ds_weekly = ds.resample(time='W').median('time')
weekly_mean = ds_weekly.mean(dim=['lat', 'lon'])
df = weekly_mean.to_dataframe()
df.plot()
df.to_csv('tss_weekly.csv')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water_quality', '0161_sen2_tss', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water_quality')  # explicit upload; requires Drive OAuth scope
