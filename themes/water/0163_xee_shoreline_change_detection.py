# Bangladesh adaptation: 0163_xee_shoreline_change_detection
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'water' / '0163_xee_shoreline_change_detection'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0087_shoreline_monitoring.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-168: Shoreline Change Detection using Landsat Missions

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
landsat7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterDate('2000', '2001').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 10)).map(lambda img: img.normalizedDifference(['SR_B2', 'SR_B4']).rename('ndwi')).median()
landsat9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2024', '2025').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 10)).map(lambda img: img.normalizedDifference(['SR_B3', 'SR_B5']).rename('ndwi')).median()
landsat9
import xarray as xr
ds7 = xr.open_dataset(landsat7, engine='ee', crs='EPSG:4326', scale=0.0003, geometry=BD_ROI)
ds7 = ds7.squeeze('time').drop_vars('time') * 1
water7 = (ds7.ndwi > 0).astype('int')
from scipy.ndimage import binary_erosion
import numpy as np
kernel = np.ones((7, 7))
kernel
erosion7 = binary_erosion(water7, structure=kernel).astype('int')
erosion7 = xr.DataArray(erosion7, dims=water7.dims, coords=water7.coords)
erosion7
shoreline7 = water7 - erosion7
shoreline7.plot(x='lon', y='lat')
ds9 = xr.open_dataset(landsat9, engine='ee', crs='EPSG:4326', scale=0.0003, geometry=BD_ROI)
ds9 = ds9.squeeze('time').drop_vars('time') * 1
water9 = (ds9.ndwi > 0).astype('int')
erosion9 = binary_erosion(water9, structure=kernel).astype('int')
erosion9 = xr.DataArray(erosion9, dims=water9.dims, coords=water9.coords)
erosion9
shoreline9 = water9 - erosion9
shoreline9.plot(x='lon', y='lat')
shoreline_changes = xr.where(shoreline7 == 1, 2000, xr.where(shoreline9 == 1, 2024, np.nan))
shoreline_changes.plot(x='lon', y='lat', cmap='rainbow')
import rioxarray
out = shoreline_changes.copy()
out = out.rio.write_crs('EPSG:4326', inplace=True)
out = out.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
out = out.rio.write_coordinate_system(inplace=True)
out = out.transpose('lat', 'lon')
out.rio.to_raster('shoreline_change.tiff')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0163_xee_shoreline_change_detection', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
