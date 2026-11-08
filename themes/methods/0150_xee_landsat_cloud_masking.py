# Bangladesh adaptation: 0150_xee_landsat_cloud_masking
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0150_xee_landsat_cloud_masking'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0070_landsat_cloud_mask.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-155: Landsat Cloud Masking using Python API (Xee)

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

def cloud_mask(img):
    qa = img.select('QA_PIXEL')
    dilated = qa.bitwiseAnd(1 << 1).neq(0)
    cirrus = qa.bitwiseAnd(2 << 1).neq(0)
    cloud = qa.bitwiseAnd(3 << 1).neq(0)
    shadow = qa.bitwiseAnd(4 << 1).neq(0)
    mask = dilated.Or(cirrus).Or(cloud).Or(shadow)
    ms = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    ndvi = ms.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
    return ndvi.updateMask(mask.Not()).copyProperties(img, ['system:time_start'])
landsat = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2024', '2025').filterBounds(roi).map(cloud_mask)
landsat
ds = xr.open_dataset(landsat, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.001)
ds = ds.sortby('time') * 1
ds.ndvi.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True)
ds_rol = ds.rolling(time=7, center=True, min_periods=1).mean('time')
ds_rol.ndvi.plot(x='lon', y='lat', col='time', robust=True, col_wrap=6)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0150_xee_landsat_cloud_masking', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
