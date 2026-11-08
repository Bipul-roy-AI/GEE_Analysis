# Bangladesh adaptation: 0189_bootcamp2026_05
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0189_bootcamp2026_05'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""05_session5_conditional_statement.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session5: Conditional Statement

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2019', '2020').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)).filterBounds(roi).select('B[2-4]', 'B8').median().multiply(0.0001)
sen2
import xarray as xr
ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=30)
ds = ds.squeeze('time').drop_vars('time') * 1
nir = ds.B8
red = ds.B4
ndvi = (nir - red) / (nir + red)
import hvplot.xarray
import numpy as np
condition1 = xr.where(ndvi < 0, 1, np.nan)
condition2 = xr.where(ndvi > 0.2, 2, condition1)
condition3 = xr.where((ndvi >= 0) & (ndvi <= 0.2), 3, condition2)
condition3.plot(x='X', y='Y')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0189_bootcamp2026_05', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
