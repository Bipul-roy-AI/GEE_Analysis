# Bangladesh adaptation: 0187_xee_hvplot
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0187_xee_hvplot'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0110_hvplot.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-189: Interactive Mapping using hvplot

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
viirs = ee.ImageCollection('NASA/VIIRS/002/VNP13A1').filterDate('2020', '2021').select('EVI')
viirs
import xarray as xr
ds = xr.open_dataset(viirs, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.1)
ds = ds.sortby('time') * 1
ds
ds_mean = ds.mean(dim='time')
import hvplot.xarray
ds_mean
ds_mean.EVI.hvplot(x='lon', y='lat', height=500, cmap='RdYlGn', robust=True, title='Average EVI - 2020')
ds_mean.EVI.hvplot.quadmesh(x='lon', y='lat', cmap='RdYlGn', robust=True, height=500)
ds_mean.EVI.hvplot.contour(x='lon', y='lat', robust=True, cmap='RdYlGn', height=500, levels=10)
ds_mean.EVI.hvplot.contourf(x='lon', y='lat', cmap='RdYlGn', robust=True, height=500, levels=20)
ds.EVI.hvplot(x='lon', y='lat', cmap='RdYlGn', robust=True, height=500, groupby='time', widget_location='bottom', widget_type='scrubber')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0187_xee_hvplot', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
