# Bangladesh adaptation: 0199_xee_l7_slcoff
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0199_xee_l7_slcoff'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00004_landsat7_slcoff_test.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-192: Landsat-7 SLC-off Correction
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi

def add_ndvi(img):
    qa_band = img.select('QA_PIXEL')
    bit1 = qa_band.bitwiseAnd(1 << 1).neq(0)
    bit3 = qa_band.bitwiseAnd(1 << 3).neq(0)
    bit4 = qa_band.bitwiseAnd(1 << 4).neq(0)
    cloud_mask = bit1.Or(bit3).Or(bit4)
    sr = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    ndvi = sr.normalizedDifference(['SR_B4', 'SR_B3']).rename('ndvi')
    return ndvi.updateMask(cloud_mask.Not()).copyProperties(img, ['system:time_start'])
landsat7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterDate('2020', '2021').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 45)).map(add_ndvi)
landsat7
import xarray as xr
ds = xr.open_dataset(landsat7, engine='ee', crs='EPSG:3857', scale=100, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds
ndvi_smooth = ds.rolling(time=4, min_periods=1, center=True).mean()
filled = ndvi_smooth.interpolate_na(dim='X', method='linear').interpolate_na(dim='Y', method='linear')
filled.ndvi.plot(x='X', y='Y', col='time', col_wrap=6, robust=True)
ndvi_smooth.ndvi.plot(x='X', y='Y', col='time', col_wrap=6, robust=True)
ds.ndvi.plot(x='X', y='Y', col='time', robust=True, col_wrap=6)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0199_xee_l7_slcoff', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
