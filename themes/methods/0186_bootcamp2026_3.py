# Bangladesh adaptation: 0186_bootcamp2026_3
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0186_bootcamp2026_3'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""03_session3_img_clip_spectral_indices.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session3: Import Shapefil and Image Clipping

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
border = BD_ROI
border
map.addLayer(border, {}, 'border')
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2025', '2026').filterBounds(border).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).select('B.*').median()

def spectral_index(img):
    sr = img.multiply(0.0001)
    ndvi = sr.normalizedDifference(['B8', 'B4']).rename('ndvi')
    ndwi = sr.normalizedDifference(['B3', 'B8']).rename('ndwi')
    return ndvi.addBands(ndwi)
sen2_index = spectral_index(sen2)
sen2_index
import xarray as xr
ds = xr.open_dataset(sen2_index, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds = ds.squeeze('time').drop_vars('time') * 1
ds.ndvi.plot(x='lon', y='lat', robust=True)
vec = geemap.ee_to_gdf(ee.FeatureCollection(border))
vec.plot()
import rioxarray
vec.crs
ds_dims = ds.rio.set_spatial_dims(x_dim='lon', y_dim='lat')
ds_clip = ds.rio.clip(vec.geometry, vec.crs)
ds_clip
ds_clip.ndvi.plot(x='lon', y='lat', robust=True, cmap='RdYlGn', levels=15)
ds.ndwi.plot(x='lon', y='lat', robust=True, cmap='Blues')
ds_clip.ndwi.plot(x='lon', y='lat', robust=True, cmap='Blues', vmin=0, vmax=1)
l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2025', '2026').filterBounds(border).select('ST_B10').filter(ee.Filter.lt('CLOUD_COVER', 20)).median().multiply(0.00341802).add(149).rename('lst')
l9
ds_lst = xr.open_dataset(l9, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
lst_cel = ds_lst.squeeze('time').drop_vars('time') - 273.15
lst_dim = lst_cel.rio.set_spatial_dims(x_dim='lon', y_dim='lat')
lst_clip = lst_dim.rio.clip(vec.geometry, vec.crs)
import matplotlib.pyplot as plt
lst_clip.lst.plot(x='lon', y='lat', robust=True, cmap='inferno')
plt.savefig('temp.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0186_bootcamp2026_3', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
