# Bangladesh adaptation: 0144_xee_pr_pca
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0144_xee_pr_pca'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0062_precipitation_pattern_pca.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-149: Precipitation Spatio-Temporal Analysis using PCA, using Python API (Xee)

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
roi = BD_ROI
roi
map = geemap.Map(basemap='SATELLITE')
map.centerObject(roi, 5)
map.addLayer(roi, {}, 'roi')
map
pr = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate('2001', '2010').map(lambda img: img.clip(roi).copyProperties(img, img.propertyNames()))
pr
ds = xr.open_dataset(pr, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.27)
ds
ds_mean = ds.mean(dim='time')
ds_mean.precipitation.plot(x='lon', y='lat', robust=True)
import xeofs as xf
pca = xf.single.EOF(n_modes=10)
pca.fit(ds, dim='time')
comp = pca.components()
comp.precipitation.plot(x='lon', y='lat', robust=True, col='mode', col_wrap=5)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0144_xee_pr_pca', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
