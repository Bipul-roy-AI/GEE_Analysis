# Bangladesh adaptation: 0139_xee_ndvi_phenology
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'agriculture' / '0139_xee_ndvi_phenology'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0053_ndvi_phenology.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-144: NDVI Phenology Analysis, in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor



"""
import ee
import geemap
import xee
import xarray as xr
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
collection = ee.ImageCollection('NOAA/CDR/AVHRR/NDVI/V5').filterDate('2016', '2017').select('NDVI').map(lambda img: img.multiply(0.0001).copyProperties(img, img.propertyNames()))
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.05, geometry=BD_ROI)
ds
df = ds.to_dataframe().reset_index()[['time', 'NDVI']].set_index('time').interpolate(method='linear')
from scipy.signal import savgol_filter
df['NDVI_smoothed'] = savgol_filter(df['NDVI'], window_length=30, polyorder=2)
df['NDVI_smoothed'].plot()
df.plot()
thresh = 0.35
sos = df['NDVI_smoothed'][df['NDVI_smoothed'] > thresh].index[0].date()
print(f'start of growing season (sos): {sos}')
eos = df['NDVI_smoothed'][df['NDVI_smoothed'] > thresh].index[-1].date()
print(f'end of growing season (eos): {eos}')
los = (eos - sos).days + 1
print(f'length of growing season (los): {los}')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0139_xee_ndvi_phenology', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
