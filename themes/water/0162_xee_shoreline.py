# Bangladesh adaptation: 0162_xee_shoreline
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'water' / '0162_xee_shoreline'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0086_shoreline.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-167: Shoreline Detection using Landsat and Sentinel

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

def oli_ndwi(img):
    ndwi = img.normalizedDifference(['SR_B3', 'SR_B5']).rename('ndwi')
    return ndwi
landsat9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2024', '2025').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 10)).map(oli_ndwi).median()
landsat9
import xarray as xr
ds = xr.open_dataset(landsat9, engine='ee', crs='EPSG:4326', scale=0.0003, geometry=BD_ROI)
ds = ds.squeeze('time').drop_vars('time') * 1
water = (ds.ndwi > 0).astype(int)
water
water.plot(x='lon', y='lat', robust=True)
ds.ndwi.plot(x='lon', y='lat', robust=True)
from scipy.ndimage import binary_erosion
import numpy as np
kernel = np.ones((7, 7))
kernel
water_eroded = binary_erosion(water.values, structure=kernel).astype('int')
water_eroded = xr.DataArray(water_eroded, coords=water.coords, dims=water.dims)
shoreline = water - water_eroded
shoreline.plot(x='lon', y='lat')
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2024', '2025').filterBounds(roi).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).map(lambda img: img.normalizedDifference(['B3', 'B8']).rename('ndwi')).median()
sen2
sen2_ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:4326', scale=0.0001, geometry=BD_ROI)
sen2_ds = sen2_ds.squeeze('time').drop_vars('time') * 1
sen2_water = (sen2_ds.ndwi > 0).astype(int)
sen2_water.plot(x='lon', y='lat')
sen2_ds.ndwi.plot(x='lon', y='lat', robust=True)
sen2_kernel = np.ones((11, 11))
sen2_eroded = binary_erosion(sen2_water.values, structure=sen2_kernel).astype('int')
sen2_eroded = xr.DataArray(sen2_eroded, coords=sen2_water.coords, dims=sen2_water.dims)
sen2_shoreline = sen2_water - sen2_eroded
sen2_shoreline.plot(x='lon', y='lat')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0162_xee_shoreline', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
