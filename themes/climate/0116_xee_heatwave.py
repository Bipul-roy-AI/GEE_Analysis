# Bangladesh adaptation: 0116_xee_heatwave
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0116_xee_heatwave'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0024_heatwave_index.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-121: Heat Wave Index, in Python API (Xee)

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
collection = ee.ImageCollection('ECMWF/ERA5/DAILY').select('maximum_2m_air_temperature').filterDate('2000', '2020').map(lambda img: img.subtract(273.15).copyProperties(img, img.propertyNames()))
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.27, geometry=BD_ROI)
ds
ds.maximum_2m_air_temperature.attrs['units'] = 'degC'
ds
import xclim
help(xclim.indices.heat_wave_index)
index = xclim.indices.heat_wave_index(ds.maximum_2m_air_temperature, thresh='25.0 degC', window=5, freq='YS')
index
index.plot(x='lon', y='lat', col='time', robust=True, col_wrap=5)
index5 = index.resample(time='5Y').max('time').rename('Heat Wave')
index5.plot(x='lon', y='lat', col='time', col_wrap=3, robust=True)
sub = index.sel(lon=24.767281538125793, lat=60.278314064805166, method='nearest')
sub
df = sub.to_dataframe()['maximum_2m_air_temperature']
import pandas as pd
df.to_csv('heat_wave.csv')
df
df.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0116_xee_heatwave', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
