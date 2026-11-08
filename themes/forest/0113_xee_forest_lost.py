# Bangladesh adaptation: 0113_xee_forest_lost
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'forest' / '0113_xee_forest_lost'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""Untitled30.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-118: Wildfire and Forest Loss, using Python API (Xee)

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
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')).filterDate('2024', '2026').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 10)).sort('system:time_start')
landsat

def ndvi(img):
    band = img.select('SR.*').multiply(2.75e-05).add(-0.2)
    index = band.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
    return index.copyProperties(img, ['system:time_start'])
landsat_ndvi = landsat.map(ndvi)
landsat_ndvi
ndvi_before = landsat_ndvi.filterDate('2024', '2025').median().rename('ndvi_before')
ndvi_after = landsat_ndvi.filterDate('2025', '2026').median().rename('ndvi_after')
ndvi_change = ndvi_before.subtract(ndvi_after).rename('ndvi_change')
ndvi_stack = ee.Image.cat([ndvi_before, ndvi_after, ndvi_change])
ndvi_stack
segmentation = ee.Algorithms.Image.Segmentation.SNIC(ndvi_stack).select('.*mean')
segmentation

def burned_area(img):
    img_thr = img.gt(0.3).selfMask()
    thr_pix = img_thr.multiply(ee.Image.pixelArea().divide(1000000.0))
    return thr_pix
forest_lost = burned_area(segmentation.select('ndvi_change_mean'))
forest_lost.reduceRegion(reducer=ee.Reducer.sum(), geometry=roi, scale=30).values().get(0)
ds = xr.open_dataset(segmentation, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.0003)
ds
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
plt.tight_layout(w_pad=2)
ds.ndvi_before_mean.plot(ax=ax[0], x='lon', y='lat', robust=True, cmap='RdYlGn')
ds.ndvi_after_mean.plot(ax=ax[1], x='lon', y='lat', robust=True, cmap='RdYlGn')
ax[0].set_title('NDVI Before')
ax[1].set_title('NDVI After')
plt.savefig('ndvi_change.png', dpi=360, bbox_inches='tight')
ds.ndvi_change_mean.plot(x='lon', y='lat', cmap='Spectral', robust=True)
thr = ds.ndvi_change_mean > 0.3
thr.plot(x='lon', y='lat', cmap='Greys')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0113_xee_forest_lost', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
