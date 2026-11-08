# Bangladesh adaptation: 0134_xee_dem_clustering
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'terrain' / '0134_xee_dem_clustering'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0049_elevation_mapping.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-139: Elevation (DEM) Mapping in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xarray as xr
import xee
import numpy as np
import pandas as pd
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
dem = ee.Image('NASA/NASADEM_HGT/001').select([0], ['elevation'])
dem
xdem = xr.open_dataset(dem, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.001)
xdem
xdem.elevation.plot(x='lon', y='lat', robust=True)
df = xdem.to_dataframe()
df
from sklearn.cluster import KMeans
model = KMeans(n_clusters=5)
model.fit(df)
df['classes'] = model.predict(df)
df
xarr = df.to_xarray().sortby(['lon', 'lat'])
xarr
xarr.classes.plot(x='lon', y='lat')
class_num = np.unique(xarr.classes.values)
class_num
xarr.elevation.where(xarr.classes == 1).mean().values
for i in class_num:
    class_mean = xarr.elevation.where(xarr.classes == i).mean().values.round(2)
    print(f'class {i} average: {class_mean}')
    class_max = xarr.elevation.where(xarr.classes == i).max().values.round(2)
    print(f'class {i} maximum: {class_max}')
    class_min = xarr.elevation.where(xarr.classes == i).min().values.round(2)
    print(f'class {i} minimum: {class_min}')
    print('-----------------------------------')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'terrain', '0134_xee_dem_clustering', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'terrain')  # explicit upload; requires Drive OAuth scope
