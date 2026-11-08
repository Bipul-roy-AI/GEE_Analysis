# Bangladesh adaptation: 0168_xee_water_deficit
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0168_xee_water_deficit'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0091_water_deficit.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-173: Water Deficit Index Mapping using Cartopy

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
mod = ee.ImageCollection('MODIS/061/MOD16A2GF').filterDate('2001', '2025').select('ET', 'PET').map(lambda img: img.select('PET').subtract(img.select('ET')).multiply(0.1).rename('wd').copyProperties(img, ['system:time_start']))
mod
import xarray as xr
ds = xr.open_dataset(mod, engine='ee', crs='EPSG:4326', scale=1, geometry=BD_ROI)
ds = ds.sortby('time') * 1
import numpy as np
ds_annual = ds.resample(time='YE').sum('time')
ds_annual_mean = ds_annual.mean(dim='time')
ds_annual_mean = xr.where(ds_annual_mean == 0, np.nan, ds_annual_mean)
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
plt.figure()
ax = plt.axes(projection=ccrs.Hammer())
ax.coastlines(resolution='110m')
ds_annual_mean.wd.plot.contourf(x='lon', y='lat', robust='True', levels=10, alpha=0.9, transform=ccrs.PlateCarree(), cmap='turbo', cbar_kwargs={'orientation': 'horizontal', 'pad': 0.05, 'shrink': 0.7, 'label': 'Water Deficit Index [mm]'})
plt.savefig('wd_map.png', dpi=360, bbox_inches='tight')
ds_annual_mean.wd.plot(x='lon', y='lat', robust=True, figsize=(10, 5))
ds

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0168_xee_water_deficit', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
