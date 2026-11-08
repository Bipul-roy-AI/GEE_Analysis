# Bangladesh adaptation: 0110_xee_irrigation_index
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'agriculture' / '0110_xee_irrigation_index'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0018_irrigation_index.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-115: Simple Irrigation Index, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap as gee
import xarray as xr
import xee
None
None
map = gee.Map(basemap='SATELLITE')
map
roi = BD_ROI
ndvi = ee.ImageCollection('MODIS/061/MOD13A2').select('NDVI').filterDate('2020', '2021').max().multiply(0.0001)
ndvi_mask = ndvi.gt(0.5)
ndvi_ds = xr.open_dataset(ndvi, engine='ee', scale=0.01, crs='EPSG:4326', geometry=BD_ROI)
ndvi_ds
ndvi_ds.NDVI.plot(x='lon', y='lat', cmap='gist_earth_r', robust=True)
thr = ndvi_ds.NDVI > 0.5
thr
thr.plot(x='lon', y='lat')
terra = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate('2020', '2021').select('aet', 'pr')

def masking(img):
    return img.updateMask(ndvi_mask).copyProperties(img, img.propertyNames())
terra_mask = terra.map(masking)
terra_ds = xr.open_dataset(terra_mask, engine='ee', scale=0.05, crs='EPSG:4326', geometry=BD_ROI)
terra_ds
terra_ds['deficit'] = terra_ds.pr - terra_ds.aet * 0.1
terra_ds
terra_ds.deficit.plot(x='lon', y='lat', cmap='coolwarm_r', robust=True, col='time', col_wrap=4, vmin=-20)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0110_xee_irrigation_index', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
