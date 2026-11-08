# Bangladesh adaptation: 0118_xee_ndvi_phenology
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'agriculture' / '0118_xee_ndvi_phenology'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-123: Vegetation Phenological Aanalysis using NDVI, in Python API (Xee)

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
ndvi = ee.ImageCollection('NOAA/CDR/VIIRS/NDVI/V1').select('NDVI', 'QA').filterDate('2021', '2022')
ndvi

def cloud_mask(img):
    ndvi_img = img.select('NDVI').multiply(0.0001)
    qa_img = img.select('QA')
    cloud = qa_img.bitwiseAnd(1 << 1).neq(0)
    shadow = qa_img.bitwiseAnd(1 << 2).neq(0)
    mask = cloud.Or(shadow).Not()
    return ndvi_img.updateMask(mask).copyProperties(img, img.propertyNames())
ndvi_mask = ndvi.map(cloud_mask)
ndvi_mask
ds = xr.open_dataset(ndvi_mask, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds
monthly = ds.resample(time='M').mean('time')
monthly
monthly.NDVI.plot(x='lon', y='lat', col='time', col_wrap=4, robust=True)
import netCDF4
ds.to_netcdf('ndvi_daily.nc')
import dea_tools.temporal
import netCDF4
import xarray as xr
ds = xr.open_dataset('ndvi_daily.nc')
ds
phenology = dea_tools.temporal.xr_phenology(ds.NDVI, stats=['SOS', 'POS', 'EOS', 'Trough', 'vSOS', 'vPOS', 'vEOS', 'LOS', 'AOS', 'ROG', 'ROS'], method_sos='first', method_eos='last', verbose=True)
phenology
phenology.SOS.plot(x='lon', y='lat', robust=True)
phenology.POS.plot(x='lon', y='lat', robust=True)
phenology.vPOS.plot(x='lon', y='lat', robust=True)
phenology.LOS.plot(x='lon', y='lat', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0118_xee_ndvi_phenology', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
