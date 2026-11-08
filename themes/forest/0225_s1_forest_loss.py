# Bangladesh adaptation: 0225_s1_forest_loss
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'forest' / '0225_s1_forest_loss'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00017_wildfire_sar.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-205: Sentinel-1 Forest Loss Change Detection
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
'# **Study Area**'
hansen = ee.Image('UMD/hansen/global_forest_change_2025_v1_13').select('loss', 'lossyear')
forest_loss23 = hansen.select('loss').eq(1).And(hansen.select('lossyear').eq(23))
import geemap
map = geemap.Map(basemap='SATELLITE')
map.addLayer(forest_loss23, {}, '2023')
map
roi = BD_ROI
roi
'# **Sentinel-1 Image Collection**'
s1 = ee.ImageCollection('OPERA/RTC/L2_V1/S1').filterDate('2022', '2024').filterBounds(roi).select('VV').filter(ee.Filter.eq('ACQUISITION_MODE', 'IW')).filter(ee.Filter.eq('ORBIT_PASS_DIRECTION', 'ascending'))
s1.size()
s1.limit(10)
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
s1.first().select('VV').projection()
grid_100m = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:32610', grid_scale=(100, -100))
ds = xr.open_dataset(s1, engine='ee', **grid_100m, chunks='auto')
ds
from dask.diagnostics import ProgressBar
with ProgressBar():
    ds = ds.sortby('time').compute()
'# **Speckel Smoothing**'
from scipy.ndimage import median_filter
ds_smooth = xr.apply_ufunc(median_filter, ds['VV'], kwargs={'size': 5}, input_core_dims=[['x', 'y']], output_core_dims=[['x', 'y']], dask='parallelized', vectorize=True, output_dtypes=[ds.VV.dtype])
'# **Forest Loss Detection**'
pre_change = ds_smooth.sel(time='2022').median('time')
post_change = ds_smooth.sel(time='2023').median('time')
change = pre_change - post_change
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(18, 5))
pre_change.plot(ax=ax[0], x='x', y='y', robust=True, cmap='turbo')
post_change.plot(ax=ax[1], x='x', y='y', robust=True, cmap='turbo')
change.plot(ax=ax[2], x='x', y='y', robust=True)
plt.tight_layout()
'# **Area of Change**'
change_pixels = (change > 0.01).astype(int).sum(dim=['x', 'y']).item()
change_pixels
import rioxarray
x_res, y_res = change.rio.resolution()
pixel_size = abs(x_res * y_res)
pixel_size
change_pixels * pixel_size / 1000000.0

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0225_s1_forest_loss', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
