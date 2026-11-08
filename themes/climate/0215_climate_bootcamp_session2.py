# Bangladesh adaptation: 0215_climate_bootcamp_session2
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0215_climate_bootcamp_session2'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""02_class2_temperature_preparation.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session2: Temperature Analysis
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
'# **Study Area**'
import geopandas as gpd
roi = gpd.read_file('iran_border.shp')
roi
import geemap
roi_ee = geemap.gdf_to_ee(roi)
roi_ee
map = geemap.Map()
map.centerObject(roi_ee, 5)
map.addLayer(roi_ee, {}, 'Iran')
map
'# **Hourly Temperature Image Collection**'
era5 = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY').filterDate('2025', '2026').select('temperature_2m')
era5.size()
era5.limit(100)
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi_ee.geometry().getInfo()), grid_crs='EPSG:4326', grid_scale=(0.11, -0.11))
ds = xr.open_dataset(era5, engine='ee', **grid_params)
ds = ds.sortby('time') - 273.15
ds
'# **Clip**'
import rioxarray
ds_clip = ds.rio.clip(roi.geometry, roi.crs)
ds_clip.isel(time=100).temperature_2m.plot.contourf(x='x', y='y', robust=True, cmap='RdBu_r', levels=10)
'# **Temporal Aggregation**'
temp_mean = ds_clip.mean(dim='time')
temp_min = ds_clip.min(dim='time')
temp_max = ds_clip.max(dim='time')
temp_max.temperature_2m.plot.contourf(x='x', y='y', robust=True, cmap='RdBu_r', levels=10)
temp_daily = ds_clip.resample(time='D').mean('time')
temp_daily.sel(time='2025-07-02').temperature_2m.plot.contourf(x='x', y='y', robust=True, cmap='RdBu_r', levels=10)
temp_daily.sel(time=slice('2025-07-02', '2025-07-15')).mean('time').temperature_2m.plot(x='x', y='y', robust=True, cmap='RdBu_r')
ds_monthly = ds_clip.resample(time='M').mean('time')
ds_monthly.temperature_2m.plot(x='x', y='y', col='time', col_wrap=4, robust=True, cmap='RdBu_r', levels=20)
temp_seasonal = ds_clip.resample(time='Q-DEC').mean('time')
temp_seasonal.temperature_2m.plot(x='x', y='y', robust=True, cmap='RdBu_r', col='time')
temp_sum = ds_clip.sum('time')
import numpy as np
temp_sum = temp_sum.where(temp_sum > 0, np.nan)
temp_sum.temperature_2m.plot.contourf(x='x', y='y', robust=True, levels=10, cmap='RdBu_r')
temp_point = ds_clip.sel(x=48.647324379693494, y=31.308809062403434, method='nearest')
temp_df = temp_point.to_dataframe()['temperature_2m']
temp_df.describe()
temp_df_daily = temp_df.resample('D').mean()
temp_df_daily.plot()
temp_df_daily.to_csv('temp_daily.csv')
temp_df.resample('M').mean().plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0215_climate_bootcamp_session2', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
