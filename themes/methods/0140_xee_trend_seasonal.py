# Bangladesh adaptation: 0140_xee_trend_seasonal
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0140_xee_trend_seasonal'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0057_trend_monitoring_seasonal_decomposition.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-145: Trend Analysis without Seasonal Impact, in Python API (Xee)

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
collection = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate('1980', '2025').select('def').map(lambda img: img.multiply(0.1).copyProperties(img, img.propertyNames()))
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.05)
ds
ds_mean = ds.mean(dim=['lon', 'lat'])
df = ds_mean.to_dataframe()
df.plot()
from statsmodels.tsa.seasonal import seasonal_decompose
model = seasonal_decompose(df['def'], model='additive', period=12)
model.plot()
plt.plot()
df_trend = model.trend
df_trend.plot()
import pymannkendall as mk
import pyhomogeneity as hg
mk_test = mk.original_test(df_trend)
hg_test = hg.pettitt_test(df_trend)
print(f'mk_test: {mk_test}')
print(f'hg_test: {hg_test}')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0140_xee_trend_seasonal', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
