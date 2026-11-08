# Bangladesh adaptation: 0136_xee_interp
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0136_xee_interp'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0051_interpolation.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-141: Temporal Interpolation for EO Products, in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor



"""
import ee
import geemap
import xee
import xarray as xr
import pandas as pd
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
collection = ee.ImageCollection('JRC/GHSL/P2023A/GHS_BUILT_S').filterBounds(roi).select('built_surface')
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.001)
ds
ds.sel(time=slice('2010', '2020')).built_surface.plot(x='lon', y='lat', col='time', robust=True)
time_start = ds.time.values[0]
time_end = ds.time.values[-1]
time_list = pd.date_range(time_start, time_end, freq='YE')
time_list
ds_annual = ds.interp(time=time_list)
ds_annual
ds_annual.sel(time=slice('2010', '2020')).built_surface.plot(x='lon', y='lat', col='time', col_wrap=5, robust=True)
ds_area = ds.sum(dim=['lat', 'lon'])
annual_area = ds_annual.sum(dim=['lat', 'lon'])
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(ds_area.time, ds_area.built_surface, marker='o')
ax.plot(annual_area.time, annual_area.built_surface, marker='o', color='tab:red', alpha=0.4)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0136_xee_interp', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
