# Bangladesh adaptation: 0196_bootcamp2026_10
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'agriculture' / '0196_bootcamp2026_10'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""10_session10_crop_phenology.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session10: Crop Phenological Metrics
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

def ndvi(img):
    fmask = img.select('Fmask')
    bit0 = fmask.bitwiseAnd(1 << 0).neq(0)
    bit1 = fmask.bitwiseAnd(1 << 1).neq(0)
    bit3 = fmask.bitwiseAnd(1 << 3).neq(0)
    cloud_mask = bit0.Or(bit1).Or(bit3)
    index = img.normalizedDifference(['B8', 'B4']).rename('ndvi')
    return index.updateMask(cloud_mask.Not()).copyProperties(img, ['system:time_start'])
sen2 = ee.ImageCollection('NASA/HLS/HLSS30/v002').filterDate('2024', '2025').filterBounds(roi).map(ndvi)
sen2
import xarray as xr
ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:3857', scale=100, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds10dys = ds.resample(time='10D').max('time')
ds10dys.ndvi.plot(x='X', y='Y', robust=True, col='time', col_wrap=7)
ds_smooth = ds10dys.rolling(time=3, center=True, min_periods=1).mean('time')
ds_smooth.ndvi.plot(x='X', y='Y', robust=True, col='time', col_wrap=7)
ndvi_peak = ds_smooth.max('time')
ndvi_peak.ndvi.plot(x='X', y='Y', robust=True)
ndvi_base = ds_smooth.min('time')
ndvi_base.ndvi.plot(x='X', y='Y', robust=True)
ndvi_amplitude = ndvi_peak - ndvi_base
ndvi_amplitude.ndvi.plot(x='X', y='Y', robust=True)
ndvi_thr = 0.2 * ndvi_amplitude + ndvi_base
ndvi_thr.ndvi.plot(x='X', y='Y', robust=True)
ndvi_above = (ds_smooth > ndvi_thr).astype(int)
ndvi_above.ndvi.plot(x='X', y='Y', col='time', col_wrap=7)
sos = ndvi_above.ndvi.idxmax('time').dt.dayofyear
sos.plot(x='X', y='Y', robust=True)
eos = ndvi_above.ndvi.isel(time=slice(None, None, -1)).idxmax('time').dt.dayofyear
eos.plot(x='X', y='Y', robust=True)
los = eos - sos
los = (eos - sos).where(eos > sos)
los.plot(x='X', y='Y', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0196_bootcamp2026_10', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
