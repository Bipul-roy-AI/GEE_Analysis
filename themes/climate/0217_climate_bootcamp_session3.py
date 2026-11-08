# Bangladesh adaptation: 0217_climate_bootcamp_session3
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0217_climate_bootcamp_session3'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""03_class3_temperature_trend_analysis.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session3: Temperature Trend Analysis
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
'# **Study Area**'
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
'# **ERA-5 Monthly Image Collection**'
collection = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate('2000', '2026').select('temperature_2m')
collection
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.11, -0.11))
ds = xr.open_dataset(collection, engine='ee', **grid_params)
ds = ds.sortby('time') - 273.15
ds
'# **Monthly Mean Temperature**'
ds_monthly = ds.mean(dim=['y', 'x']).to_dataframe()
ds_monthly.plot()
from statsmodels.tsa.seasonal import STL
ds_monthly
stl_model = STL(ds_monthly, period=12)
stl_fit = stl_model.fit()
import matplotlib.pyplot as plt
stl_fit.plot()
plt.show()
temp_trend = stl_fit.trend
temp_trend.plot()
import pymannkendall as mk
import pyhomogeneity as ph
mk.original_test(temp_trend)
ph.pettitt_test(temp_trend)
'# **Trend Visualization**'
import matplotlib.pyplot as plt
from datetime import datetime
fig, ax = plt.subplots(figsize=(8, 2.5))
ax.plot(ds_monthly.index, ds_monthly, label='original', alpha=0.3)
ax.set_title('Temperature Trend (Tehran)')
ax.set_ylabel('Monthly Temperature [cel]')
ax.set_xlabel('Monthly')
ax.tick_params(axis='both', direction='in')
ax.legend()
ax1 = ax.twinx()
ax1.plot(temp_trend.index, temp_trend, color='tab:red', label='Trend Temperature')
ax1.set_ylabel('Trend Temperature [cel]')
ax1.tick_params(axis='both', direction='in')
ax1.legend()
ax1.vlines(ymin=temp_trend.min(), ymax=temp_trend.max(), x=datetime(2014, 3, 1), ls='--', color='black')
ax1.text(y=13.5, x=datetime(2015, 1, 1), s='BP: 2014-03-01')
plt.savefig('temp_trend.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0217_climate_bootcamp_session3', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
