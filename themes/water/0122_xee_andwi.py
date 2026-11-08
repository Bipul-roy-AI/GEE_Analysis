# Bangladesh adaptation: 0122_xee_andwi
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'water' / '0122_xee_andwi'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0033_andwi.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-127: Augmented Normalized Difference Water Index, using Python API (Xee)

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
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')).filterBounds(roi).filterDate('2024', '2025').sort('system:time_start')
landsat

def water_index(img):
    qa = img.select('QA_PIXEL')
    cirrus = qa.bitwiseAnd(1 << 2).neq(0)
    cloud = qa.bitwiseAnd(1 << 3).neq(0)
    shadow = qa.bitwiseAnd(1 << 4).neq(0)
    mask = cirrus.Or(cloud).Or(shadow).Not()
    bands = img.select('SR.*').multiply(2.75e-05).add(-0.2).updateMask(mask)
    if index_name == 'ndwi':
        ndwi = bands.normalizedDifference(['SR_B3', 'SR_B5']).rename('ndwi')
        return ndwi.copyProperties(img, ['system:time_start'])
    elif index_name == 'andwi':
        andwi = bands.expression('(blue + green + red - nir - swir1 - swir2)/(blue + green + red + nir + swir1 + swir2)', {'blue': bands.select('SR_B2'), 'green': bands.select('SR_B3'), 'red': bands.select('SR_B4'), 'nir': bands.select('SR_B5'), 'swir1': bands.select('SR_B6'), 'swir2': bands.select('SR_B7')}).rename('andwi')
        return andwi.copyProperties(img, ['system:time_start'])
index_name = 'ndwi'
ndwi = landsat.map(water_index)
index_name = 'andwi'
andwi = landsat.map(water_index)
ndwi_ds = xr.open_dataset(ndwi, engine='ee', crs='EPSG:4326', scale=0.003, geometry=BD_ROI)
andwi_ds = xr.open_dataset(andwi, engine='ee', crs='EPSG:4326', scale=0.003, geometry=BD_ROI)
ndwi_mean = ndwi_ds.mean('time')
andwi_mean = andwi_ds.mean('time')
ndwi_mean.ndwi.plot(x='lon', y='lat', robust=True)
andwi_mean.andwi.plot(x='lon', y='lat', robust=True)
ndwi_monthly = ndwi_ds.resample(time='M').mean('time')
andwi_monthly = andwi_ds.resample(time='M').mean('time')
ndwi_monthly.ndwi.plot(x='lon', y='lat', col='time', robust=True, col_wrap=4)
andwi_monthly.andwi.plot(x='lon', y='lat', col='time', robust=True, col_wrap=4)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0122_xee_andwi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
