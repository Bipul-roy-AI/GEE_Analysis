# Bangladesh adaptation: 0218_climate_bootcamp_session4
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0218_climate_bootcamp_session4'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""04_class4_precipitation_anomaly_detection.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session4: Precipitation Anomaly Detection
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
point = BD_ROI
point
roi = BD_ROI
map.addLayer(roi, {}, 'Iran')
'# **ERA5 Precipitation Image Collection**'
collection = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate('2000', '2026').select(['total_precipitation_sum'], ['pr'])
collection
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.11, -0.11))
ds = xr.open_dataset(collection, engine='ee', **grid_params)
ds = ds.sortby('time') * 1000
'# **Clip**'
import geopandas as gpd
roi_gdf = geemap.ee_to_gdf(ee.FeatureCollection(roi))
import rioxarray
ds_clip = ds.rio.clip(roi_gdf.geometry, roi_gdf.crs)
ds_clip
'# **Annual Precipitation**'
pr_annual = ds_clip.resample(time='YS').sum('time')
import numpy as np
pr_annual_mask = pr_annual.where(pr_annual > 0, np.nan)
pr_annual_mask.pr.plot.contourf(x='x', y='y', robust=True, col='time', col_wrap=7, cmap='turbo_r', levels=10)
'# **Anomaly Mapping**'
pr_mean = pr_annual_mask.mean('time')
pr_anomaly = pr_annual_mask - pr_mean
pr_anomaly.pr.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, col_wrap=7, col='time')
pr_std = pr_annual_mask.std('time')
pr_std.pr.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10)
pr_anomaly_stan = (pr_annual_mask - pr_mean) / pr_std
import matplotlib.pyplot as plt
pr_anomaly_stan.pr.plot.contourf(x='x', y='y', robust=True, col='time', cmap='turbo_r', levels=10, col_wrap=7)
plt.savefig('pr_anomaly.png', dpi=360, bbox_inches='tight')
pr_annual_change = pr_annual_mask.diff('time')
pr_annual_change.pr.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, col='time', col_wrap=7)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0218_climate_bootcamp_session4', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
