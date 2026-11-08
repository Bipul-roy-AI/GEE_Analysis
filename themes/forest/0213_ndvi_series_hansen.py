# Bangladesh adaptation: 0213_ndvi_series_hansen
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'forest' / '0213_ndvi_series_hansen'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""Untitled0.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutotrial-201: Froest Loss Time Series Analysis using MODIS NDVI and Hansen Product
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
'# **Study Area**'
forest = ee.Image('UMD/hansen/global_forest_change_2025_v1_13').select('loss', 'lossyear')
loss_area = forest.select('loss').eq(1).And(forest.select('lossyear').eq(15))
import geemap
map = geemap.Map(basemap='SATELLITE')
map.addLayer(loss_area, {}, 'loss_area')
map
roi = BD_ROI
roi
'# **MODIS NDVI Image Collection**'
modis = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate('2000', '2026').select('NDVI')
modis
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:3857', grid_scale=(250, -250))
ds = xr.open_dataset(modis, engine='ee', **grid_params)
ds = ds.sortby('time') * 0.0001
'# **NDVI Time Series**'
ds_mean = ds.mean(dim=['x', 'y']).to_dataframe()
ds_mean.plot()
'# **Trend Analysis**'
from statsmodels.tsa.seasonal import STL
stl_model = STL(ds_mean, period=24)
stl_result = stl_model.fit()
ndvi_trend = stl_result.trend
ndvi_trend.plot()
import pymannkendall as mk
import pyhomogeneity as hg
mk_test = mk.original_test(ndvi_trend)
hg_test = hg.pettitt_test(ndvi_trend)
print(mk_test)
print(hg_test)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0213_ndvi_series_hansen', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
