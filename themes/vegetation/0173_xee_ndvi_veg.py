# Bangladesh adaptation: 0173_xee_ndvi_veg
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'vegetation' / '0173_xee_ndvi_veg'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0096_correlation_ndvi_analysis.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-178: Vegetation (NDVI) Response to Precipitation Analysis

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
time_start = ee.Date('2010')
time_end = ee.Date('2026')
time_dif = time_end.difference(time_start, 'month').round()
time_list = ee.List.sequence(0, ee.Number(time_dif).subtract(1)).map(lambda t: time_start.advance(t, 'month'))
pr = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate(time_start, time_end).select('precipitation')
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate(time_start, time_end).select('NDVI')

def monthly(date_list, col):
    start_date = ee.Date(date_list)
    end_date = start_date.advance(1, 'month')
    col_agg = col.filterDate(start_date, end_date).median()
    return col_agg.set('system:time_start', start_date.millis())
ndvi_monthly = ee.ImageCollection(time_list.map(lambda d: monthly(d, ndvi)))
pr_monthly = ee.ImageCollection(time_list.map(lambda d: monthly(d, pr)))

def bandnum(img):
    img_size = img.bandNames().size()
    return img.set('band_size', ee.Number(img_size))
pr_monthly = pr_monthly.map(bandnum).filter(ee.Filter.eq('band_size', 1))
ndvi_monthly = ndvi_monthly.map(bandnum).filter(ee.Filter.eq('band_size', 1))
collection = ndvi_monthly.combine(pr_monthly)
collection
import xarray as xr
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.05)
ds
ds = ds.sortby('time') * 1
ds
cor = xr.corr(ds.NDVI, ds.precipitation, dim='time')
cor.plot(x='lon', y='lat', robust=True)
cor3 = xr.corr(ds.NDVI, ds.precipitation.shift(time=3), dim='time')
cor3.plot(x='lon', y='lat', robust=True)
lag_list = [1, 2, 3, 4, 5, 6, 7]
cor_list = []
for lag in lag_list:
    cor_lag = xr.corr(ds.NDVI, ds.precipitation.shift(time=lag), dim='time')
    cor_list.append(cor_lag)
cor_stack = xr.concat(cor_list, dim='lag')
cor_stack = cor_stack.assign_coords(lag=lag_list)
cor_stack.plot(x='lon', y='lat', robust=True, col='lag', col_wrap=4)
cor_stack.idxmax(dim='lag').plot(x='lon', y='lat', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0173_xee_ndvi_veg', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
