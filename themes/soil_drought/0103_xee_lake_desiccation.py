# Bangladesh adaptation: 0103_xee_lake_desiccation
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0103_xee_lake_desiccation'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0011_lake_desiccation.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-108: Lake Mapping, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!

"""
import ee
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import xee
None
None
mod = ee.ImageCollection('MODIS/061/MOD09A1').select('sur_refl_b02', 'sur_refl_b04').filterDate('2001', '2025')
loc = BD_ROI
ds = xr.open_dataset(mod, engine='ee', crs='EPSG:4326', scale=0.01, geometry=BD_ROI)
ds
green = ds.sur_refl_b04 * 0.0001
nir = ds.sur_refl_b02 * 0.0001
nir
ndwi = (green - nir) / (green + nir)
ndwi
ndwi_annual = ndwi.resample(time='YE').mean('time')
ndwi_annual
ndwi_annual.plot(x='lon', y='lat', cmap='Blues', col='time', col_wrap=5, robust=True)
plt.savefig('lake_desiccation.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0103_xee_lake_desiccation', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
