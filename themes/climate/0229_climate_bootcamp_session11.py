# Bangladesh adaptation: 0229_climate_bootcamp_session11
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0229_climate_bootcamp_session11'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""11_class11_mannkendall.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session11: Spatio - Temporal Monitoring
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
map = geemap.Map()
map
roi = BD_ROI
roi
'# **ERA Image Collection**'
era = ee.ImageCollection('ECMWF/ERA5/MONTHLY').filterDate('1980', '2020').select(['mean_2m_air_temperature'], ['mean_temp'])
era
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_50km = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.5, -0.5))
ds = xr.open_dataset(era, engine='ee', **grid_50km)
ds = ds.sortby('time') - 273.15
ds
'# **Trend Monitoring**'
import pymannkendall as mk
import numpy as np

def mann_kendall_test(x):
    x = x[~np.isnan(x)]
    if len(x) < 3:
        return (np.nan, np.nan, np.nan, np.nan)
    mk_test = mk.original_test(x)
    trend = {'increasing': 1, 'decreasing': -1, 'no trend': 0}[mk_test.trend]
    return (trend, mk_test.p, mk_test.slope, mk_test.z)
trend, pval, slope, zscore = xr.apply_ufunc(mann_kendall_test, ds[['mean_temp']], input_core_dims=[['time']], output_core_dims=[[], [], [], []], vectorize=True, dask='parallelized', output_dtypes=[float, float, float, float])
map1 = xr.where((trend == 1) & (pval < 0.05), slope, np.nan)
map1.mean_temp.plot(x='x', y='y', robust=True, cmap='turbo')
map2 = xr.where((trend == 1) & (pval < 0.05), zscore, np.nan)
map2.mean_temp.plot(x='x', y='y', robust=True, cmap='turbo', edgecolor='face', alpha=0.8)
'# **Trend Monitoring without Seasonal Impact**'

def mann_kendall_test2(x):
    x = x[~np.isnan(x)]
    if len(x) < 12 * 2:
        return (np.nan, np.nan, np.nan, np.nan)
    mk_test = mk.seasonal_test(x, period=12)
    trend = {'increasing': 1, 'decreasing': -1, 'no trend': 0}[mk_test.trend]
    return (trend, mk_test.p, mk_test.slope, mk_test.z)
trend, pval, slope, zscore = xr.apply_ufunc(mann_kendall_test2, ds[['mean_temp']], input_core_dims=[['time']], output_core_dims=[[], [], [], []], vectorize=True, dask='parallelized', output_dtypes=[float, float, float, float])
map3 = xr.where((trend == 1) & (pval < 0.05), slope, np.nan)
map3.mean_temp.plot(x='x', y='y', robust=True, cmap='turbo', edgecolor='face', alpha=0.8)
map4 = xr.where((trend == 1) & (pval < 0.05), zscore, np.nan)
map4.mean_temp.plot(x='x', y='y', robust=True, cmap='turbo', edgecolor='face', alpha=0.8)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0229_climate_bootcamp_session11', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
