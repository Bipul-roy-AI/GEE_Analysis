# Bangladesh adaptation: 0155_evaporation_viirs
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0155_evaporation_viirs'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0078_water_evaporation.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-160: Water Evaporation Mapping and Monitoring using VIIRS Mission

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
roi = BD_ROI
roi
lc = ee.ImageCollection('MODIS/061/MCD12Q1').select('LC_Type1').mode().eq(17)
map.addLayer(lc.clip(roi), {}, 'lc')
viirs = ee.ImageCollection('projects/usgs-ssebop/viirs_et_v6_monthly').filterDate('2015', '2025').map(lambda x: x.updateMask(lc).copyProperties(x, x.propertyNames()))
ds = xr.open_dataset(viirs, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.01)
ds = ds.sortby('time') * 1
ds.isel(time=10).et.plot(x='lon', y='lat', robust=True, vmin=35)
import numpy as np
ds_annual = ds.resample(time='Y').sum('time')
ds_annual = xr.where(ds_annual == 0, np.nan, ds_annual)
import matplotlib.pyplot as plt
ds_annual.et.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, robust=True, cmap='rainbow', vmin=1000, levels=20)
plt.savefig('annual_evaporation.png', dpi=360, bbox_inches='tight')
ds_annual.mean(dim=['lat', 'lon']).to_dataframe().to_csv('lake_evaporation.csv')
ds_annual.mean(dim=['lat', 'lon']).to_dataframe().plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0155_evaporation_viirs', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
