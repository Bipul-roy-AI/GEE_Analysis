# Bangladesh adaptation: 0108_xee_sen_slope
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0108_xee_sen_slope'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0016_sen_slope.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-113: Sen Slope Trend Analysis, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap as gee
import xarray as xr
import xee
None
None
collection = ee.ImageCollection('ECMWF/ERA5/MONTHLY').select('mean_2m_air_temperature').filterDate('2000', '2024')
map = gee.Map(basemap='SATELLITE')
map
roi = BD_ROI
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.27, geometry=BD_ROI)
ds
annual = ds.resample(time='YE').mean('time')
annual
annual.mean_2m_air_temperature.plot(x='lon', y='lat', cmap='jet', robust=True, col='time', col_wrap=7)
import pymannkendall as mk
import numpy as np

def sen_fun(img):
    clean = img[~np.isnan(img)]
    return mk.original_test(clean).slope
sen_slope_map = xr.apply_ufunc(sen_fun, ds.mean_2m_air_temperature, input_core_dims=[['time']], output_dtypes=[float], vectorize=True, dask='allows')
sen_slope_map
sen_slope_map.plot(x='lon', y='lat', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0108_xee_sen_slope', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
