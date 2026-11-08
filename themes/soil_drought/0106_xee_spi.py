# Bangladesh adaptation: 0106_xee_spi
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0106_xee_spi'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0014_spi.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-111: Standardized Precipitation Index, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import xarray as xr
import xee
None
None
time_start = ee.Date('2000')
time_end = ee.Date('2024')
time_dif = time_end.difference(time_start, 'month').round()
time_list = ee.List.sequence(0, ee.Number(time_dif).subtract(1), 1).map(lambda x: time_start.advance(x, 'month'))
col = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate(time_start, time_end)

def monthly(date):
    start_date = ee.Date(date)
    end_date = start_date.advance(1, 'month')
    img = col.filterDate(start_date, end_date).sum()
    return img.set('system:time_start', start_date.millis())
monthly_col = ee.ImageCollection(time_list.map(monthly))
loc = [42.49229836400454, 25.412218155914445, 64.99229836400454, 40.18617527857037]
ds = xr.open_dataset(monthly_col, engine='ee', crs='EPSG:4326', scale=0.27, geometry=BD_ROI)
ds
annual = ds.resample(time='YE').sum('time')
annual
import matplotlib.pyplot as plt
annual.precipitation.plot(x='lon', y='lat', cmap='jet_r', col='time', robust=True, col_wrap=5)
point = ds.sel(lon=48.29307961400454, lat=32.92450826905307, method='nearest')
point
point.time.values
point.precipitation.values
plt.plot(point.time, point.precipitation)
from standard_precip import spi
import pandas as pd
date = point.time.values
pr = point.precipitation.values
df = pd.DataFrame({'date': date, 'pr': pr})
df
spi_fun = spi.SPI()
spi_12months = spi_fun.calculate(df, 'date', 'pr', freq='M', scale=12, fit_type='lmom', dist_type='gam')
spi_12months.to_csv('spi_12month.csv')
spi_12months
from standard_precip.utils import plot_index
fig = plot_index(spi_12months, 'date', 'pr_scale_12_calculated_index')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0106_xee_spi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
