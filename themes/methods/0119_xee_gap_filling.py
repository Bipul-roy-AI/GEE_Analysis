# Bangladesh adaptation: 0119_xee_gap_filling
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0119_xee_gap_filling'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-124: Cloud Gap Filling, in Python API (Xee)

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
ndvi = ee.ImageCollection('NOAA/CDR/VIIRS/NDVI/V1').select('NDVI', 'QA').filterDate('2020', '2021')
ndvi

def cloud_mask(img):
    index = img.select('NDVI').multiply(0.0001)
    qa = img.select('QA')
    cloud = qa.bitwiseAnd(1 << 1).neq(0)
    shadow = qa.bitwiseAnd(1 << 2).neq(0)
    mask = cloud.Or(shadow).Not()
    return index.updateMask(mask).copyProperties(img, img.propertyNames())
ndvi_masked = ndvi.map(cloud_mask)
ndvi_masked
ds = xr.open_dataset(ndvi_masked, engine='ee', crs='EPSG:4326', scale=0.05, geometry=BD_ROI)
ds
sub = ds.sel(time=ds.time.dt.month == 1)
sub
sub.NDVI.plot(x='lon', y='lat', col='time', col_wrap=8, robust=True, cmap='RdYlGn')
point = ds.sel(lon=49.398480435524995, lat=37.26737308003883, time=ds.time.dt.month == 1, method='nearest')
point.NDVI.plot()
rolling = ds.rolling(time=10, min_periods=1, center=True).mean()
ds_filled = ds.fillna(rolling)
sub2 = ds_filled.sel(time=ds_filled.time.dt.month == 1)
import matplotlib.pyplot as plt
sub2.NDVI.plot(x='lon', y='lat', col='time', col_wrap=8, robust=True, cmap='RdYlGn')
plt.savefig('ndvi_filled.png', dpi=360, bbox_inches='tight')
point2 = ds_filled.sel(lon=49.398480435524995, lat=37.26737308003883, time=ds.time.dt.month == 1, method='nearest')
point2.NDVI.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0119_xee_gap_filling', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
