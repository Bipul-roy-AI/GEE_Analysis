# Bangladesh adaptation: 0149_xee_water_storage
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0149_xee_water_storage'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0069_water_storage_monitoring.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-154: Water Storage Mapping and Monitoring using GRACE in Xee Library

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xarray as xr
import xee
None
None
map = geemap.Map(basemap='SATELLITE')
map
loc = BD_ROI
loc
iran = BD_ROI
map.addLayer(iran, {}, 'Iran')
collection = ee.ImageCollection('NASA/GRACE/MASS_GRIDS_V04/MASCON_CRI').filterDate('2003', '2024').select('lwe_thickness').map(lambda img: img.clip(iran).copyProperties(img, img.propertyNames()))
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=1)
ds = ds.sortby('time') * 1
ds_month = ds.groupby('time.month').mean('time')
ds_month
ds_month.lwe_thickness.plot.contourf(x='lon', y='lat', col='month', robust=True, col_wrap=4, cmap='turbo_r', levels=20)
ds_annual = ds.resample(time='Y').mean('time')
ds_annual
ds_annual.lwe_thickness.plot.contourf(x='lon', y='lat', col='time', cmap='turbo_r', robust=True, col_wrap=5, levels=20)
ds_mean = ds_annual.mean('time')
ds_anomaly = ds_annual - ds_mean
import matplotlib.pyplot as plt
ds_anomaly.lwe_thickness.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, robust=True, cmap='turbo_r', levels=20)
plt.savefig('water_storage_anomaly.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0149_xee_water_storage', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
