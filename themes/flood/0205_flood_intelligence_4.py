# Bangladesh adaptation: 0205_flood_intelligence_4
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'flood' / '0205_flood_intelligence_4'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""04_session4_floody_precipitation.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Flood Intelligence Workshop - Session4: Floody Precipitation Event
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

# **Connect to GEE**
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
country = BD_COUNTRY
map.addLayer(country, {}, 'Iran')
'# **Precipitation Image Collection**'
pr = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate('2010', '2022').select(['precipitation'], ['pr'])
pr
'# **Image Collection to Xarray**'
from shapely.geometry import shape
country_shape = shape(country.getInfo())
country_shape
from xee import helpers
grid_params = helpers.fit_geometry(geometry=country_shape, grid_crs='EPSG:4326', grid_scale=(0.3, -0.3))
import xarray as xr
ds = xr.open_dataset(pr, engine='ee', **grid_params)
ds = ds.sortby('time') * 1
'# **Clipping**'
import rioxarray
country_gdf = geemap.ee_to_gdf(ee.FeatureCollection(country))
country_gdf.plot()
ds.isel(time=101).pr.plot(x='x', y='y', robust=True)
ds_clip = ds.rio.clip(country_gdf.geometry, country_gdf.crs)
ds_clip.isel(time=101).pr.plot(x='x', y='y', robust=True)
'# **Precipitation and Flood**'
pr_annual = ds_clip.resample(time='YE').sum('time')
import numpy as np
pr_anomaly = pr_annual - pr_annual.mean(dim='time')
pr_anomaly = pr_anomaly.where(pr_anomaly != 0, np.nan)
pr_anomaly.pr.plot.contourf(x='x', y='y', robust=True, col_wrap=6, cmap='turbo_r', col='time', levels=12)
pr_monthly = ds_clip.resample(time='M').sum('time')
pr_month = pr_monthly.groupby('time.month').mean('time')
pr_month = pr_month.where(pr_month != 0, np.nan)
pr_month.pr.plot.contourf(x='x', y='y', robust=True, col='month', col_wrap=6, cmap='turbo_r', levels=12)
pr_flood = pr_monthly.sel(time='2019')
pr_flood = pr_flood.where(pr_flood != 0, np.nan)
pr_flood.pr.plot.contourf(x='x', y='y', robust=True, col='time', col_wrap=6, cmap='turbo_r', levels=12)
ds_clip.sel(time='2019-04').pr.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=12, col='time', col_wrap=7)
ds_clip.mean(dim='time').pr.plot(x='x', y='y')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'flood', '0205_flood_intelligence_4', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'flood')  # explicit upload; requires Drive OAuth scope
