# Bangladesh adaptation: 0157_xee_sen2_cyanobacteria
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'water_quality' / '0157_xee_sen2_cyanobacteria'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0080_sen2_cyano.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-162: Sentinel-2 Water Cyanobacteria Index using Python API (Xee)

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

def cyano_index(img):
    cloud = img.select('probability')
    cloud_free = cloud.lt(20)
    sr = img.select('B.*').multiply(0.0001)
    ndwi = sr.normalizedDifference(['B3', 'B8']).rename('ndwi')
    water = ndwi.gt(0.1)
    cyano = sr.expression('115530.31 * (((b3 * b4)/b2) ** 2.38)', {'b2': sr.select('B2'), 'b3': sr.select('B3'), 'b4': sr.select('B4')}).rename('cyano')
    return cyano.updateMask(water).updateMask(cloud_free).copyProperties(img, ['system:time_start'])
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').linkCollection(ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY'), 'probability').filterDate('2024', '2025').filterBounds(roi).map(cyano_index)
sen2
ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds_monthly = ds.resample(time='M').mean('time')
ds_monthly
import matplotlib.pyplot as plt
ds_monthly.cyano.plot(x='lon', y='lat', col='time', cmap='rainbow', robust=True, col_wrap=6, vmax=200)
plt.savefig('sen2_cyano.png', dpi=360, bbox_inches='tight')
ds_mean = ds_monthly.mean(dim=['lat', 'lon'])
df = ds_mean.to_dataframe()
df.to_csv('sen2_cyano.csv')
df.plot(marker='o', figsize=(7, 3))
plt.savefig('sen2_cyano_graph.png', bbox_inches='tight', dpi=360)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water_quality', '0157_xee_sen2_cyanobacteria', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water_quality')  # explicit upload; requires Drive OAuth scope
