# Bangladesh adaptation: 0167_xee_lake_ice_cover
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'snow' / '0167_xee_lake_ice_cover'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0090_ice_lake.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-172: Lake Ice Cover Monitoring using Sentinel-1

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
lake = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate('2024', '2025').filterBounds(roi).filter(ee.Filter.calendarRange(6, 9, 'month')).select('label').mode().eq(0).selfMask()
sen1 = ee.ImageCollection('COPERNICUS/S1_GRD').filterDate('2022', '2024').filterBounds(roi).filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')).filter(ee.Filter.eq('instrumentMode', 'IW')).select('VV').filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING')).map(lambda img: img.updateMask(lake).copyProperties(img, ['system:time_start']))
sen1
map.addLayer(lake.clip(roi), {}, 'lake')
import xarray as xr
ds = xr.open_dataset(sen1, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds_roll = ds.rolling(time=10, center=True, min_periods=1).mean('time')
ds_weekly = ds_roll.resample(time='W').mean('time')
ds_weekly.mean(dim=['lat', 'lon']).to_dataframe().plot()
plot = ds_weekly.VV.plot(x='lon', y='lat', col='time', col_wrap=10, cmap='turbo', robust=True)
for x in plot.axes.flat:
    x.set_title(x.get_title(), fontsize=15)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'snow', '0167_xee_lake_ice_cover', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'snow')  # explicit upload; requires Drive OAuth scope
