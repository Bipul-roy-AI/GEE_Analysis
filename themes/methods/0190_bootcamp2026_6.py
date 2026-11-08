# Bangladesh adaptation: 0190_bootcamp2026_6
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0190_bootcamp2026_6'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""06_session6_change_detection.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session6: Change Detection

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
landsat5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterDate('1984', '1990').filterBounds(roi).select('SR_B.*').filter(ee.Filter.lt('CLOUD_COVER', 10)).median()
landsat5
import xarray as xr
ds_l5 = xr.open_dataset(landsat5, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=1000)
ds_l5 = ds_l5.squeeze('time').drop_vars('time') * 2.75e-05 + -0.2
ndwi = ((ds_l5.SR_B2 - ds_l5.SR_B4) / (ds_l5.SR_B2 + ds_l5.SR_B4)).rename('ndwi1990')
ndwi.plot(x='X', y='Y', robust=True)
landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2020', '2026').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 10)).select('SR_B.*').median()
landsat8
ds_l8 = xr.open_dataset(landsat8, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=1000)
ds_l8 = ds_l8.squeeze('time').drop_vars('time') * 2.75e-05 + -0.2
ndwi2 = ((ds_l8.SR_B3 - ds_l8.SR_B5) / (ds_l8.SR_B3 + ds_l8.SR_B5)).rename('ndwi2025')
ndwi2.plot(x='X', y='Y', robust=True)
change1 = ndwi - ndwi2
change1.plot(x='X', y='Y', robust=True)
change2 = (ndwi2 - ndwi) / (ndwi2 + ndwi)
change2.plot(x='X', y='Y', robust=True)
import numpy as np
condition = xr.where(ndwi > 0.1, 1990, np.nan)
condition2 = xr.where(ndwi2 > 0.1, 2025, condition)
condition2.plot(x='X', y='Y')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
plt.tight_layout(w_pad=5)
plot1 = ndwi.plot(x='X', y='Y', robust=True, cmap='Blues', ax=ax[0])
ax[0].set_title('Urmia Lake - 1990')
plot2 = ndwi2.plot(x='X', y='Y', robust=True, cmap='Blues', ax=ax[1])
ax[1].set_title('Urmia Lake - 2025')
plot3 = change2.plot(x='X', y='Y', robust=True, ax=ax[2])
ax[2].set_title('Change in Urmia Lake 1990 - 2025')
plt.savefig('lake_plot.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0190_bootcamp2026_6', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
