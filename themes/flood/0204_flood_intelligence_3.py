# Bangladesh adaptation: 0204_flood_intelligence_3
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'flood' / '0204_flood_intelligence_3'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""03_session3_landsat_flood.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Flood Intelligence Workshop - Session3: Flood Detection and Mapping using Landsat
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
'# **Study Area**'
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
'# **Landsat Image Collection**'

def ndvi(img):
    qa_band = img.select('QA_PIXEL')
    bit1 = qa_band.bitwiseAnd(1 << 1).neq(0)
    bit2 = qa_band.bitwiseAnd(1 << 2).neq(0)
    bit3 = qa_band.bitwiseAnd(1 << 3).neq(0)
    bit4 = qa_band.bitwiseAnd(1 << 4).neq(0)
    mask = bit1.Or(bit2).Or(bit3).Or(bit4)
    sr = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    index = sr.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
    return index.updateMask(mask.Not()).copyProperties(img, ['system:time_start'])
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2015', '2020').filterBounds(roi).filter(ee.Filter.eq('WRS_PATH', 163)).filter(ee.Filter.eq('WRS_ROW', 34))
landsat_ndvi = landsat.map(ndvi)
landsat_ndvi
'# **Image Collection to Xarray**'
landsat.first().select('SR_B1').projection()
from shapely.geometry import shape
vec = shape(roi.getInfo())
vec
from xee import helpers
grid_params = helpers.fit_geometry(geometry=vec, grid_crs='EPSG:32639', grid_scale=(100, -100))
import xarray as xr
ds = xr.open_dataset(landsat_ndvi, engine='ee', **grid_params)
ds = ds.sortby('time') * 1
'# **Flood Analysis**'
ds_month = ds.groupby('time.month').max(dim='time')
ds_month.ndvi.plot(x='x', y='y', col='month', col_wrap=6, cmap='RdYlGn', robust=True)
ds.sel(time='2019').ndvi.plot(x='x', y='y', col='time', col_wrap=5, cmap='RdYlGn', robust=True)
flood = ds.sel(time='2019-04').squeeze('time').drop_vars('time')
flood.ndvi.plot(x='x', y='y', robust=True, cmap='RdYlGn')
flood_thr = (flood.ndvi > 0.7).astype(int)
flood_thr.plot(x='x', y='y')
import rioxarray
x_res, y_res = flood.rio.resolution()
pixel_size = abs(x_res * y_res)
pixel_size
(flood_thr == 1).sum(dim=['y', 'x']).item() * pixel_size / 1000000.0
ref = ds_month.sel(month=4).drop_vars('month')
ref
ref.ndvi.plot(x='x', y='y', robust=True, cmap='RdYlGn')
ref_thr = (ref.ndvi > 0.7).astype(int)
ref_thr.plot(x='x', y='y')
(ref_thr == 1).sum(dim=['y', 'x']).item() * pixel_size / 1000000.0

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'flood', '0204_flood_intelligence_3', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'flood')  # explicit upload; requires Drive OAuth scope
