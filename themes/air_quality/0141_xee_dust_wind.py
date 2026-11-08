# Bangladesh adaptation: 0141_xee_dust_wind
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'air_quality' / '0141_xee_dust_wind'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0058_dust_wind.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-146: Dust and Wind Association Analysis, in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xee
import xarray as xr
import matplotlib.pyplot as plt
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
pm = ee.ImageCollection('projects/sat-io/open-datasets/GLOBAL-SATELLITE-PM25/MONTHLY').select([0], ['pm']).filterDate('2010', '2015')
vs = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select('vs').filterDate('2010', '2015').map(lambda img: img.multiply(0.01).copyProperties(img, ['system:time_start']))
join = ee.Join.inner()
filter = ee.Filter.equals(leftField='system:time_start', rightField='system:time_start')
join_col = ee.ImageCollection(join.apply(pm, vs, filter))
collection = join_col.map(lambda el: ee.Image.cat(el.get('primary'), el.get('secondary')))
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds
ds_mean = ds.mean(dim=['lat', 'lon'])
ds_mean
df = ds_mean.to_dataframe()
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(df.index, df.pm)
ax1 = ax.twinx()
ax1.bar(df.index, df.vs, color='red', width=10, alpha=0.2)
df.corr()
plt.scatter(df.pm, df.vs)
import statsmodels.api as sm
x = df.vs.values
y = df.pm.values
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
print(model.summary())

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'air_quality', '0141_xee_dust_wind', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'air_quality')  # explicit upload; requires Drive OAuth scope
