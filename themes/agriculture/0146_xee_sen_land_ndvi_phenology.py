# Bangladesh adaptation: 0146_xee_sen_land_ndvi_phenology
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'agriculture' / '0146_xee_sen_land_ndvi_phenology'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0064_crop_phenolgical_metrics.ipynb


utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-151: Landsat-Sentinel Crop Phenological Analysis, in Python API (Xee)

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

def index(img):
    qa_band = img.select('Fmask')
    cirrus = qa_band.bitwiseAnd(1 << 0).neq(0)
    cloud = qa_band.bitwiseAnd(1 << 1).neq(0)
    shadow = qa_band.bitwiseAnd(1 << 3).neq(0)
    mask = cirrus.Or(cloud).Or(shadow)
    ndvi = img.normalizedDifference(['B8', 'B4']).rename('ndvi')
    return ndvi.updateMask(mask.Not()).copyProperties(img, ['system:time_start'])
collection = ee.ImageCollection('NASA/HLS/HLSS30/v002').filterDate('2024', '2025').filterBounds(roi).map(index)
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.0003, geometry=BD_ROI)
ds = ds.sortby('time')
ds_rol = ds.rolling(time=10, center=True, min_periods=1).median('time')
ds_10days = ds_rol.resample(time='10D').median('time')
ds_10days.ndvi.plot(x='lon', y='lat', col='time', col_wrap=7, cmap='RdYlGn', robust=True)
ndvi_peak = ds_10days.max('time')
ndvi_base = ds_10days.min('time')
ndvi_amplitude = ndvi_peak - ndvi_base
ndvi_thr = 0.2 * ndvi_amplitude + ndvi_base
ndvi_abov = (ds_10days > ndvi_thr).astype(int)
sos = ndvi_abov.ndvi.idxmax('time').dt.dayofyear
eos = ndvi_abov.ndvi.isel(time=slice(None, None, -1)).idxmax('time').dt.dayofyear
los = eos - sos
los = xr.where(los < 0, los + 365, los)
los.plot(x='lon', y='lat', robust=True)
ndvi_abov.ndvi.plot(x='lon', y='lat', col='time', col_wrap=7)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0146_xee_sen_land_ndvi_phenology', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
