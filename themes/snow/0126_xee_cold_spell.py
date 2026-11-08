# Bangladesh adaptation: 0126_xee_cold_spell
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'snow' / '0126_xee_cold_spell'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0038_cold_spell.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-131: Cold Spell Detection and Monitoring, in Python API (Xee)

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
map = geemap.Map(basemap='TERRAIN')
map
roi = BD_ROI
roi
temp = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate('2010', '2015').select(['mean_2m_air_temperature'], ['temp_air'])
temp
ds = xr.open_dataset(temp, engine='ee', crs='EPSG:4326', scale=0.11, geometry=BD_ROI)
ds = ds - 273.15
annual = ds.resample(time='YE').mean('time')
annual
annual.temp_air.plot(x='lon', y='lat', col='time', col_wrap=3, robust=True)
import xclim
import xclim.indices as xindices
help(xindices.cold_spell_days)
ds.temp_air.attrs['units'] = 'degC'
ds
cs_days = xindices.cold_spell_days(ds.temp_air, thresh='-10 degC', window=5, freq='YS-JUL')
cs_days.plot(x='lon', y='lat', col='time', col_wrap=3)
help(xindices.cold_spell_frequency)
cs_freq = xindices.cold_spell_frequency(ds.temp_air, thresh='-10 degC', window=5, freq='YS-JUL')
cs_freq.plot(x='lon', y='lat', col='time', col_wrap=3)
help(xindices.cold_spell_max_length)
cs_max_length = xindices.cold_spell_max_length(ds.temp_air, thresh='-10 degC', window=1, freq='YS-JUL')
cs_max_length.plot(x='lon', y='lat', col='time', col_wrap=3)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'snow', '0126_xee_cold_spell', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'snow')  # explicit upload; requires Drive OAuth scope
