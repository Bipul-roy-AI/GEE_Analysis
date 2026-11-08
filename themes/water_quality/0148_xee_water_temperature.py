# Bangladesh adaptation: 0148_xee_water_temperature
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'water_quality' / '0148_xee_water_temperature'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0068_water_temperature.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-153: Water Temperature Estimation using Landsat-8 and Landsat-9

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

def oli(img):
    qa = img.select('QA_PIXEL')
    cloud = qa.bitwiseAnd(1 << 1).neq(0)
    cirrus = qa.bitwiseAnd(2 << 1).neq(0)
    cloud2 = qa.bitwiseAnd(3 << 1).neq(0)
    shadow = qa.bitwiseAnd(4 << 1).neq(0)
    cloud_mask = cloud.Or(cirrus).Or(cloud2).Or(shadow)
    ms = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    ndwi = ms.normalizedDifference(['SR_B3', 'SR_B5']).rename('ndwi')
    water_mask = ndwi.gt(0.1)
    lst = img.select('ST_B10').multiply(0.00341802).add(149)
    return lst.updateMask(water_mask).updateMask(cloud_mask.Not()).copyProperties(img, ['system:time_start'])
l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2024', '2025').filterBounds(roi).map(oli)
l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2024', '2025').filterBounds(roi).map(oli)
collection = l8.merge(l9).sort('system:time_start')
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.0003, geometry=BD_ROI)
ds = ds.sortby('time') - 273.15
ds_roll = ds.rolling(time=7, center=True, min_periods=1).mean('time')
import matplotlib.pyplot as plt
ds_roll.sel(time=ds.time.dt.month == 7).ST_B10.plot(x='lon', y='lat', col='time', col_wrap=3, robust=True, cmap='turbo')
plt.savefig('water_temp.png', dpi=360, bbox_inches='tight')
ds.sel(time=ds.time.dt.month == 7).ST_B10.plot(x='lon', y='lat', col='time', col_wrap=3, robust=True)
ds_mean = ds_roll.mean(['lon', 'lat']).to_dataframe()
ds_mean.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water_quality', '0148_xee_water_temperature', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water_quality')  # explicit upload; requires Drive OAuth scope
