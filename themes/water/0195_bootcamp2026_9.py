# Bangladesh adaptation: 0195_bootcamp2026_9
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'water' / '0195_bootcamp2026_9'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""Untitled0.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session9: Lake Area Monitoring
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
time_start = ee.Date('2014')
time_end = ee.Date('2027')

def ndwi(img):
    qa_band = img.select('QA_PIXEL')
    bit1 = qa_band.bitwiseAnd(1 << 1).neq(0)
    bit2 = qa_band.bitwiseAnd(1 << 2).neq(0)
    bit3 = qa_band.bitwiseAnd(1 << 3).neq(0)
    bit4 = qa_band.bitwiseAnd(1 << 4).neq(0)
    mask = bit1.Or(bit2).Or(bit3).Or(bit4)
    sr = img.select('SR.*').multiply(2.75e-05).add(-0.2)
    index = sr.normalizedDifference(['SR_B3', 'SR_B5']).rename('ndwi')
    return index.updateMask(mask.Not()).copyProperties(img, ['system:time_start'])
landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(time_start, time_end).filterBounds(roi).map(ndwi)
landsat9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate(time_start, time_end).filterBounds(roi).map(ndwi)
collection = landsat8.merge(landsat9).sort('system:time_start')
import xarray as xr
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:3857', scale=1000, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds_monthly = ds.resample(time='M').max('time')
ds_monthly.sel(time='2021').ndwi.plot(x='X', y='Y', col='time', col_wrap=6, robust=True)
ds_smooth = ds_monthly.rolling(time=3, center=True, min_periods=1).mean('time')
ds_smooth.sel(time='2021').ndwi.plot(x='X', y='Y', robust=True, col='time', col_wrap=6)
ds_int = ds_smooth.interpolate_na(dim='time', method='linear')
ds_int.sel(time='2021').ndwi.plot(x='X', y='Y', col='time', col_wrap=6, robust=True)
ds_water = (ds_int > 0.3).astype(int)
ds_water.sel(time='2021').ndwi.plot(x='X', y='Y', col='time', col_wrap=6)
import rioxarray
ds_water = ds_water.rio.set_spatial_dims(x_dim='X', y_dim='Y')
x_res, y_res = ds_water.rio.resolution()
pixel_area = abs(x_res * y_res)
pixel_area_km2 = pixel_area / 1000000.0
pixel_area_km2
water_pixels = ds_water.sum(dim=['X', 'Y']).to_dataframe()
water_area = water_pixels * 1
water_area.plot()
water_area.to_csv('water_area.csv')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 2))
ax.plot(water_area.index, water_area, ls=':', marker='o', ms=4)
ax.set_ylabel('Area (km²)')
ax.set_title('Urmia Lake')
ax.grid(alpha=0.5, ls=':')
ax.tick_params(axis='both', direction='in', top=True, right=True)
plt.savefig('lake_area.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0195_bootcamp2026_9', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
