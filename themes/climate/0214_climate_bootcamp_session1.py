# Bangladesh adaptation: 0214_climate_bootcamp_session1
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0214_climate_bootcamp_session1'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""01_class1_precipitation_preparation.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session1: Precipitation Analysis
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
iran = BD_ROI
map.addLayer(iran, {}, 'Iran')
'# **Precipitation Image Collection**'
pr = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').filterDate('2020', '2026').select('total_precipitation_sum')
pr
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(iran.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.11, -0.11))
ds = xr.open_dataset(pr, engine='ee', **grid_params)
ds = ds.sortby('time') * 1000
ds
'# **Clip**'
import rioxarray
iran_gdf = geemap.ee_to_gdf(ee.FeatureCollection(iran))
ds_clip = ds.rio.clip(iran_gdf.geometry, iran_gdf.crs)
'# **Precipitation Analysis**'
pr_mean = ds_clip.mean(dim='time')
pr_max = ds_clip.max(dim='time')
pr_min = ds_clip.min(dim='time')
pr_max.total_precipitation_sum.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10)
pr_annual = ds_clip.resample(time='YE').sum('time')
pr_annual.total_precipitation_sum.plot.contourf(x='x', y='y', robust=True, col='time', col_wrap=3, cmap='turbo_r', levels=15)
pr_monthly = ds_clip.groupby('time.month').mean('time')
pr_monthly.total_precipitation_sum.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, col='month', col_wrap=6)
pr_season = ds_clip.groupby('time.season').mean('time')
import matplotlib.pyplot as plt
pr_season.total_precipitation_sum.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, col='season')
plt.savefig('pr_seasonal.png', dpi=360, bbox_inches='tight')
pr_point = ds_clip.sel(x=45.90897209076619, y=36.96423791062324, method='nearest')
pr_daily_df = pr_point.to_dataframe()['total_precipitation_sum']
pr_daily_df.to_csv('pr_daily.csv')
pr_monthly_df = pr_daily_df.resample('M').sum()
pr_monthly_df.plot()
pr_annual = pr_daily_df.resample('YE').sum()
pr_annual.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0214_climate_bootcamp_session1', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
