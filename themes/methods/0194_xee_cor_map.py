# Bangladesh adaptation: 0194_xee_cor_map
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0194_xee_cor_map'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00002_correlation_mapping.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-191: Pointwise Correlation Mapping

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
time_start = ee.Date('2017')
time_end = ee.Date('2022')
smap = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/005').filterDate(time_start, time_end).select('soil_moisture_am')
pr = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate(time_start, time_end).select('precipitation')
pr
import xarray as xr
ds_pr = xr.open_dataset(pr, engine='ee', geometry=BD_ROI, crs='EPSG:4326', scale=0.1)
ds_pr = ds_pr.sortby('time') * 1
ds_pr
ds_smap = xr.open_dataset(smap, engine='ee', geometry=BD_ROI, crs='EPSG:4326', scale=0.1)
ds_smap = ds_smap.sortby('time') * 1
smap_monthly = ds_smap.resample(time='MS').mean('time')
smap_monthly
sm_aligned, pr_aligned = xr.align(smap_monthly['soil_moisture_am'], ds_pr['precipitation'], join='inner', exclude=['lat', 'lon'])
pr_regridded = pr_aligned.interp(lat=sm_aligned.lat, lon=sm_aligned.lon, method='nearest')
pr_regridded
cor_map = xr.corr(sm_aligned, pr_regridded, dim='time')
cor_map.plot(x='lon', y='lat', robust=True, cmap='jet')
from scipy import stats

def spearman(x, y):
    c_map, p_map = stats.spearmanr(x, y)
    return (c_map, p_map)
c_map, p_map = xr.apply_ufunc(spearman, sm_aligned, pr_regridded, input_core_dims=[['time'], ['time']], output_core_dims=[[], []], vectorize=True, dask='parallelized', output_dtypes=[float, float])
import numpy as np
cmap_val = xr.where(p_map <= 0.05, c_map, np.nan)
cmap_val.plot(x='lon', y='lat', robust=True, cmap='jet')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0194_xee_cor_map', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
