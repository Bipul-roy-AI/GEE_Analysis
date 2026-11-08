# Bangladesh adaptation: 0135_xee_esi
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'soil_drought' / '0135_xee_esi'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0050_Evaporative_Stress_Index.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-140: Evaporative Stress Index in Python API (Xee)

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
import matplotlib.pyplot as plt
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
iran = BD_ROI
map.addLayer(iran, {}, 'Iran')
collection = ee.ImageCollection('projects/climate-engine/esi/12wk').filterDate('2001', '2025').map(lambda img: img.clip(iran).copyProperties(img, img.propertyNames()))
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.1)
ds
ds.isel(time=100).ESI.plot(x='lon', y='lat', robust=True)
lat = 37.06016443230056
lon = 45.95842739971374
point = ds.sel(lat=lat, lon=lon, method='nearest')
point.ESI.plot()
df = point.to_dataframe().ESI
df
pos = df[df >= 0]
neg = df[df < 0]
fig, ax = plt.subplots(figsize=(9, 3))
ax.plot(df.index, df, color='black', lw=0.5)
ax.bar(pos.index, pos, color='tab:blue', width=20)
ax.bar(neg.index, neg, color='red', width=20)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0135_xee_esi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
