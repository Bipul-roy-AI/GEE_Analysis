# Bangladesh adaptation: 0127_xee_wetland_detection
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'water' / '0127_xee_wetland_detection'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0039_wetland_mapping.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-132: Wetland Detection and Mapping, in Python API (Xee)

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
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2020', '2024').filterBounds(roi).filter(ee.Filter.lt('CLOUD_COVER', 45))
landsat
landsat_mean = landsat.select('SR_B.*').mean()
landsat_mean
ds = xr.open_dataset(landsat_mean, engine='ee', crs='EPSG:4326', scale=0.003, geometry=BD_ROI)
ds = ds * 2.75e-05 + -0.2
nir = ds.SR_B5
red = ds.SR_B4
swir2 = ds.SR_B7
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
plt.tight_layout(w_pad=4)
nir.plot(x='lon', y='lat', robust=True, ax=ax[0])
swir2.plot(x='lon', y='lat', robust=True, ax=ax[1])
ndvi = (nir - red) / (nir + red)
ndvi.plot(x='lon', y='lat', robust=True)
green = ds.SR_B3
ndwi = (green - nir) / (green + nir)
ndwi.plot(x='lon', y='lat', robust=True)
wiw = (nir <= 0.1735) & (swir2 <= 0.1035)
wiw.plot(x='lon', y='lat')
wiw = (nir <= 0.1735) | (swir2 <= 0.1035)
wiw.plot(x='lon', y='lat')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0127_xee_wetland_detection', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
