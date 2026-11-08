# Bangladesh adaptation: 0153_xee_aridity_index
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0153_xee_aridity_index'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0073_aridity_index.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-158: Climate Aridity Index using Python API (Xee)

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
time_start = ee.Date('2005')
time_end = ee.Date('2025')
time_dif = time_end.difference(time_start, 'year').round()
time_list = ee.List.sequence(0, ee.Number(time_dif).subtract(1)).map(lambda x: time_start.advance(x, 'year'))

def annual(date, col):
    start_date = ee.Date(date)
    end_date = start_date.advance(1, 'year')
    img_sum = col.filterDate(start_date, end_date).sum()
    return img_sum.set('system:time_start', start_date.millis())
gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate(time_start, time_end).select('precipitation').map(lambda x: x.multiply(730).copyProperties(x, ['system:time_start']))
mod = ee.ImageCollection('MODIS/061/MOD16A2GF').filterDate(time_start, time_end).select('PET').map(lambda x: x.multiply(0.1).copyProperties(x, ['system:time_start']))
gpm_annual = ee.ImageCollection(time_list.map(lambda x: annual(x, gpm)))
mod_annual = ee.ImageCollection(time_list.map(lambda x: annual(x, mod)))
collection = gpm_annual.combine(mod_annual)
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds
aridity = ds.precipitation / ds.PET
import matplotlib.pyplot as plt
aridity.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, robust=True, levels=10, cmap='turbo_r')
plt.savefig('aridity_map.png', dpi=360, bbox_inches='tight')
import numpy as np
aridity_map = xr.where(aridity < 0.05, 1, xr.where(aridity < 0.2, 2, xr.where(aridity < 0.5, 3, xr.where(aridity < 1, 4, np.nan))))
aridity_map.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, cmap='turbo_r')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0153_xee_aridity_index', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
