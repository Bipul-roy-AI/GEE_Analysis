# Bangladesh adaptation: 0165_xee_npp_crop
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'agriculture' / '0165_xee_npp_crop'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0089_crop_production.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-170: Crop Production Analysis using MODIS NPP Product

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
crop = ee.ImageCollection('MODIS/061/MCD12Q1').filterDate('2001', '2025').select('LC_Type1').map(lambda img: img.eq(12).copyProperties(img, ['system:time_start']))
npp = ee.ImageCollection('MODIS/061/MOD17A3HGF').filterDate('2001', '2025').select('Npp')
collection = npp.linkCollection(crop, 'LC_Type1').map(lambda img: img.select('Npp').multiply(0.0001).updateMask(img.select('LC_Type1')).copyProperties(img, ['system:time_start']))
collection
import xarray as xr
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds
total_npp = ds.sum(dim=['lat', 'lon'])
df = total_npp.to_dataframe()
df.plot()
df.to_csv('total_npp.csv')
import pymannkendall as mk
import pyhomogeneity as hg
mk_test = mk.original_test(df)
mk_test
hg_test = hg.pettitt_test(df)
hg_test
ds.Npp.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True, cmap='turbo')
import numpy as np

def spatial_change(img):
    valid_data = img[~np.isnan(img)]
    if len(valid_data) < 2:
        return np.nan
    return mk.original_test(valid_data).slope
npp_change = xr.apply_ufunc(spatial_change, ds.Npp, input_core_dims=[['time']], vectorize=True, dask='parallelized', output_dtypes=[float])
npp_change.plot(x='lon', y='lat', robust=True, cmap='turbo')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0165_xee_npp_crop', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
