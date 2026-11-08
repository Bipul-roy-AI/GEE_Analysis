# Bangladesh adaptation: 0188_bootcamp2026_04
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'water' / '0188_bootcamp2026_04'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""04_session4_veg_water_mask.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session4: Vegetation and Water Mask

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
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2020', '2022').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 5)).select('SR_B.*').median().multiply(2.75e-05).add(-0.2)
landsat
import xarray as xr
ds = xr.open_dataset(landsat, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=30)
ds = ds.squeeze('time').drop_vars('time') * 1
nir = ds.SR_B5
red = ds.SR_B4
ndvi = ((nir - red) / (nir + red)).rename('ndvi')
ndvi
import hvplot.xarray
ndvi.hvplot(x='X', y='Y', robust=True, height=500, cmap='RdYlGn')
veg_mask = (ndvi > 0.2).astype(int)
veg_mask.plot(x='X', y='Y')
import numpy as np
ndvi_veg = xr.where(veg_mask == 1, ndvi, np.nan)
ndvi_veg.plot(x='X', y='Y', robust=True)
import rioxarray
veg_mask2 = veg_mask.rio.set_spatial_dims(x_dim='X', y_dim='Y')
veg_pixels = (veg_mask2 == 1).sum(dim=['Y', 'X']).item()
x_res, y_res = veg_mask2.rio.resolution()
pixel_area = abs(x_res * y_res)
veg_area = veg_pixels * pixel_area
veg_area / 1000000.0
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2020', '2021').filterBounds(roi).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)).select('B[2-4]', 'B8').median()
sen2
ds2 = xr.open_dataset(sen2, engine='ee', crs='EPSG:3857', scale=10, geometry=BD_ROI)
ds2 = ds2.squeeze('time').drop_vars('time') * 0.0001
nir = ds2.B8
green = ds2.B3
ndwi = ((green - nir) / (green + nir)).rename('ndwi')
ndwi.hvplot(x='X', y='Y', cmap='Blues', robust=True, height=500)
water_mask = (ndwi > 0.3).astype(int)
water_mask.plot(x='X', y='Y')
ndwi_water = xr.where(water_mask == 1, ndwi, np.nan)
ndwi_water.plot(x='X', y='Y')
water_mask = water_mask.rio.set_spatial_dims(x_dim='X', y_dim='Y')
water_pixels = (water_mask == 1).sum(dim=['Y', 'X']).item()
water_pixels
x_res2, y_res2 = water_mask.rio.resolution()
pixel_size2 = abs(x_res2 * y_res2)
pixel_size2
water_area = water_pixels * pixel_size2
water_area / 1000000.0

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0188_bootcamp2026_04', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
