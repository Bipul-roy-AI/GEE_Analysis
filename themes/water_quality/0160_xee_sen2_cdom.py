# Bangladesh adaptation: 0160_xee_sen2_cdom
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'water_quality' / '0160_xee_sen2_cdom'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0083_sen2_cdom.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-165:  Sentinel-2 Colored Dissolved Organic Matter for Water Bodies

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

def index(img):
    cloud_band = img.select('probability')
    clear_pixel = cloud_band.lt(20)
    ms_bands = img.select('B.*').multiply(0.0001)
    ndwi = ms_bands.normalizedDifference(['B3', 'B8']).rename('ndwi')
    water_body = ndwi.gt(0.1)
    cdom = ms_bands.expression('537 * exp(-2.93 * (B03/B04))', {'B03': ms_bands.select('B3'), 'B04': ms_bands.select('B4')}).rename('cdom')
    return cdom.updateMask(clear_pixel).updateMask(water_body).copyProperties(img, ['system:time_start'])
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').linkCollection(ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY'), 'probability').filterDate('2024', '2025').filterBounds(roi).map(index)
sen2
import xarray as xr
ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds
ds = ds.sortby('time') * 1
ds_monthly = ds.resample(time='M').median('time')
import matplotlib.pyplot as plt
ds_monthly.cdom.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True, cmap='turbo')
plt.savefig('cdom.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water_quality', '0160_xee_sen2_cdom', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water_quality')  # explicit upload; requires Drive OAuth scope
