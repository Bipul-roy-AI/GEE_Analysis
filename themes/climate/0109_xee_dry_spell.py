# Bangladesh adaptation: 0109_xee_dry_spell
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0109_xee_dry_spell'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0017_dry_spell.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-114: Precipitation Dry Spell Analysis, using Python API (Xee)

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
map = gee.Map(basemap='SATELLITE')
map
roi = BD_ROI
collection = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate('2020', '2022')
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.27)
ds
seasonal = ds.resample(time='Q').sum('time')
seasonal
seasonal.precipitation.plot(x='lon', y='lat', col='time', robust=True, col_wrap=4, cmap='Spectral')
point = ds.sel(lon=52.6632665918151, lat=36.54071077336493, method='nearest')
point
pr = point.precipitation.values
time = point.time.values
import pandas as pd
df = pd.DataFrame({'time': time, 'pr': pr})
df
df['dry'] = df['pr'] == 0
df
df['group'] = (df['dry'] != df['dry'].shift()).cumsum()
df
dry_spell = df[df['dry']].groupby('group').agg(start_date=('time', 'first'), end_date=('time', 'last'), duration=('time', 'count'), intensity=('pr', 'sum'))
dry_spell[dry_spell['duration'] > 10]
result = dry_spell[dry_spell['duration'] > 10]
result.to_csv('dry_spell.csv')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0109_xee_dry_spell', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
