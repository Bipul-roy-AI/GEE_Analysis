# Bangladesh adaptation: 0238_modis_totram
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0238_modis_totram'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00027_modis_sm.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-214: MODIS Soil Moisture Estimation using NDVI and LST (TOTRAM)
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
'# **Study Area**'
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
'# **MODIS Products**'
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate('2025', '2026').select('NDVI')
ndvi
lst = ee.ImageCollection('MODIS/061/MOD11A2').filterDate('2025', '2026').select('LST_Day_1km')
lst
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_250m = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:3857', grid_scale=(250, -250))
ds_ndvi = xr.open_dataset(ndvi, engine='ee', **grid_250m)
ds_ndvi = ds_ndvi.sortby('time') * 0.0001
ds_lst = xr.open_dataset(lst, engine='ee', **grid_250m)
ds_lst = ds_lst.sortby('time') * 0.02
'# **Preview**'
ndvi_mean = ds_ndvi.mean(dim='time')
lst_mean = ds_lst.mean(dim='time')
ds = xr.merge([ndvi_mean, lst_mean])
ds
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ds.NDVI.plot(ax=ax[0], robust=True)
ds.LST_Day_1km.plot(ax=ax[1], robust=True)
plt.tight_layout()
'# **TOTRAM**'
import numpy as np
x = ds.NDVI.values.flatten()
x = x[~np.isnan(x)]
x = x.reshape(-1, 1)
x
y = ds.LST_Day_1km.values.flatten()
y = y[~np.isnan(y)]
y
idx = np.random.choice(len(x), 10000, replace=False)
idx
x_sample = x[idx]
y_sample = y[idx]
from sklearn.linear_model import QuantileRegressor
dry_edge = QuantileRegressor(quantile=0.95, alpha=0).fit(x_sample, y_sample)
s_d = dry_edge.coef_[0]
i_d = dry_edge.intercept_
wet_edge = QuantileRegressor(quantile=0.05, alpha=0).fit(x_sample, y_sample)
s_w = wet_edge.coef_[0]
i_w = wet_edge.intercept_
sm = (i_d + s_d * ds.NDVI - ds.LST_Day_1km) / (i_d - i_w + (s_d - s_w) * ds.NDVI)
sm = sm.clip(0, 1)
sm.plot(robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0238_modis_totram', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
