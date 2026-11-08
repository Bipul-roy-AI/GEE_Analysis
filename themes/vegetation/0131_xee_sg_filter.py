# Bangladesh adaptation: 0131_xee_sg_filter
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'vegetation' / '0131_xee_sg_filter'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0046_ndvi_daily.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-136: Savitsky Golay Filter, in Python API

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xarray as xr
import xee
import numpy as np
import xrscipy.signal as xrs
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
ndvi_collection = ee.ImageCollection('MODIS/MOD09GA_006_NDVI').filterDate('2020', '2021')
ndvi_collection
ndvi_ds = xr.open_dataset(ndvi_collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.005)
ndvi_ds
ndvi_ds.sel(time=ndvi_ds.time.dt.month == 5).NDVI.plot(x='lon', y='lat', col='time', col_wrap=7, robust=True, cmap='RdYlGn')
ndvi_ds.mean(dim=['lon', 'lat']).NDVI.plot()
ndvi_ds2 = ndvi_ds.copy()
ndvi_time = ndvi_ds2.time.values.copy()
ndvi_ds2
ndvi_ds2.coords['time'] = np.arange(len(ndvi_ds2.time))
ndvi_ds2
ndvi_smooth = xrs.savgol_filter(ndvi_ds2.NDVI, window_length=30, polyorder=2, dim='time')
ndvi_smooth.coords['time'] = ndvi_time
ndvi_smooth.sel(time=ndvi_smooth.time.dt.month == 5).plot(x='lon', y='lat', col='time', col_wrap=7, robust=True, cmap='RdYlGn')
ndvi_smooth.mean(dim=['lon', 'lat']).plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0131_xee_sg_filter', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
