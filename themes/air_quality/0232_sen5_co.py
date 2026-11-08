# Bangladesh adaptation: 0232_sen5_co
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'air_quality' / '0232_sen5_co'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00021_co_monitoring.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-208: Sentinel-5 Carbon Monoxide Data Analysis in Python
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
'# **Sentinel-5 CO Image Collection**'
co = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO').filterDate('2020', '2026').filterBounds(roi).select(['CO_column_number_density'], ['co_index'])
co.size()
co.limit(100)
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_7km = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.07, -0.07))
ds = xr.open_dataset(co, engine='ee', **grid_7km)
ds = ds.sortby('time') * 1
ds
co_mean = ds.mean(dim='time')
co_mean.co_index.plot.contourf(x='x', y='y', robust=True, cmap='turbo', levels=20)
ds_month = ds.groupby('time.month').mean('time')
ds_month.co_index.plot.contourf(x='x', y='y', robust=True, col='month', col_wrap=6, cmap='turbo', levels=10)
ds_annual = ds.resample(time='YE').mean('time')
ds_annual.co_index.plot(x='x', y='y', robust=True, cmap='turbo', col='time', levels=15, edgecolor='face', alpha=0.8, col_wrap=3)
ds_daily = ds.resample(time='1D').mean('time')
ds_daily
co_point = ds_daily.sel(x=51.381874738205106, y=35.699985606523974, method='nearest')
co_df = co_point.to_dataframe()['co_index']
thr = co_df.quantile(0.95)
extreme = co_df[co_df > thr]
extreme
extreme.describe()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(co_df.index, co_df)
ax.scatter(extreme.index, extreme, color='red')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'air_quality', '0232_sen5_co', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'air_quality')  # explicit upload; requires Drive OAuth scope
