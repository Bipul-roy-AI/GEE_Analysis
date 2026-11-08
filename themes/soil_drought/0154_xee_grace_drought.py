# Bangladesh adaptation: 0154_xee_grace_drought
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'soil_drought' / '0154_xee_grace_drought'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0077_GRACE_Drought_Index.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-159: GRACE Drought Index using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor




"""
import ee
import geemap
import xee
import xarray as xr
import numpy as np
None
None
map = geemap.Map(basemap='TERRAIN')
map
point = BD_ROI
iran = BD_ROI
map.addLayer(iran, {}, 'Iran')
grace = ee.ImageCollection('NASA/GRACE/MASS_GRIDS_V04/MASCON_CRI').filterDate('2003', '2025').select('lwe_thickness').map(lambda img: img.clip(iran).copyProperties(img, img.propertyNames()))
grace
ds = xr.open_dataset(grace, engine='ee', crs='EPSG:4326', scale=1, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds_mean = ds.mean(dim='time')
ds_std = ds.std(dim='time')
gdsi = (ds - ds_mean) / ds_std

def classify(val):
    if val >= 2.0:
        return 1
    elif val >= 1.6:
        return 2
    elif val >= 1.3:
        return 3
    elif val >= 0.8:
        return 4
    elif val >= 0.5:
        return 5
    elif val >= -0.5:
        return 6
    elif val >= -0.8:
        return 7
    elif val >= -1.3:
        return 8
    elif val >= -1.6:
        return 9
    elif val >= -2.0:
        return 10
    else:
        return 0
drought = xr.apply_ufunc(np.vectorize(classify), gdsi, dask='allowed')
drought = xr.where(drought == 0, np.nan, drought)
drought_annual = drought.resample(time='Y').median('time')
import matplotlib.pyplot as plt
drought_annual.lwe_thickness.plot.contourf(x='lon', y='lat', col='time', col_wrap=8, cmap='turbo', levels=20)
plt.savefig('annual_drought.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0154_xee_grace_drought', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
