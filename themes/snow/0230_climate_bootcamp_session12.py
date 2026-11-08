# Bangladesh adaptation: 0230_climate_bootcamp_session12
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'snow' / '0230_climate_bootcamp_session12'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""12_class12_snow_monitoring.ipynb
Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session12: Snow Season Monitoring
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
'# **ERA5 Snow Cover Image Collection**'
era = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').filterDate('2010', '2026').select('snow_cover')
era.size()
era.limit(100)
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_30km = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.3, -0.3))
ds = xr.open_dataset(era, engine='ee', **grid_30km, chunks='auto')
from dask.diagnostics import ProgressBar
with ProgressBar():
    ds = ds.compute()
ds = ds.sortby('time')
ds
'# **Snow Cover Duration**'
import xclim.indicators.land as xindex
help(xindex.snw_season_length)
ds.snow_cover.attrs['units'] = 'kg m-2'
ds
snow_duration = xindex.snw_season_length(snw=ds['snow_cover'], thresh='20 kg m-2')
snow_duration
snow_duration.plot(x='x', y='y', robust=True, cmap='turbo_r', col='time', col_wrap=6)
duration_diff = snow_duration.diff(dim='time')
duration_diff.plot.contourf(x='x', y='y', robust=True, col='time', col_wrap=6, levels=15)
duration_diff_median = duration_diff.median(dim='time')
duration_diff_median.plot.contourf(x='x', y='y', robust=True, levels=15)
'# **Mann - Kendall Trend Analysis**'
import pymannkendall as mk
import numpy as np

def mk_test(x):
    x = x[~np.isnan(x)]
    if len(x) < 3:
        return (np.nan, np.nan, np.nan)
    test = mk.original_test(x)
    trend = {'increasing': 1, 'decreasing': -1, 'no trend': 0}[test.trend]
    return (trend, test.p, test.slope)
snow_trend, snow_p, snow_slope = xr.apply_ufunc(mk_test, snow_duration, input_core_dims=[['time']], output_core_dims=[[], [], []], vectorize=True, dask='parallelized', output_dtypes=[float, float, float])
map = xr.where((snow_trend == -1) & (snow_p < 0.05), snow_slope, np.nan)
map.plot(x='x', y='y', robust=True, cmap='turbo_r')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'snow', '0230_climate_bootcamp_session12', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'snow')  # explicit upload; requires Drive OAuth scope
