# Bangladesh adaptation: 0180_xee_temp_agg
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0180_xee_temp_agg'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0104_xarray_temp_resampling.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-185: Temporal Aggregation in Python

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor
"""
import ee
None
None
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
pr = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate('2015', '2024')
pr
import xarray as xr
ds = xr.open_dataset(pr, engine='ee', crs='EPSG:4326', scale=0.3, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds
ds_monthly = ds.resample(time='M').sum('time')
ds_monthly.sel(time='2020').precipitation.plot(x='lon', y='lat', col='time', robust=True, col_wrap=6, cmap='turbo')
ds_weekly = ds.resample(time='W').sum('time')
ds_weekly
ds_weekly.sel(time=slice('2020-01', '2020-03')).precipitation.plot(x='lon', y='lat', col='time', robust=True, col_wrap=7, cmap='turbo')
ds_3days = ds.resample(time='3D').sum('time')
mean_3days = ds_3days.mean(dim=['lon', 'lat']).to_dataframe().precipitation
ds_monthly.mean(dim=['lon', 'lat']).precipitation.plot()
mean_3days.plot()
ds_yearly = ds.resample(time='YE').sum('time')
ds_yearly.precipitation.plot(x='lon', y='lat', col='time', col_wrap=3, robust=True)
ds_month = ds_monthly.groupby('time.month').mean('time')
ds_month.precipitation.plot(x='lon', y='lat', col='month', col_wrap=6, robust=True, cmap='turbo_r')
ds_month.mean(dim=['lon', 'lat']).to_dataframe().plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0180_xee_temp_agg', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
