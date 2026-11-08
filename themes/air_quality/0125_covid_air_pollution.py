# Bangladesh adaptation: 0125_covid_air_pollution
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'air_quality' / '0125_covid_air_pollution'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0037_covid_air_quality.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-130: Covid and Air Pollution, in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

Original file is located at
    https://colab.research.google.com/drive/1wxQXGFMsYEuq0QrYrS3nIUTBXXTbCaKo
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
nitrogen = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2').filterDate('2018', '2025').filterBounds(roi).select(['NO2_column_number_density'], ['no2'])
nitrogen.first()
ds = xr.open_dataset(nitrogen, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds
annual = ds.resample(time='YE').mean('time')
annual
import matplotlib.pyplot as plt
annual.no2.plot(x='lon', y='lat', col='time', col_wrap=3, robust=True)
plt.savefig('annual_no2.png', dpi=360, bbox_inches='tight')
annual_mean = annual.mean(dim=['lon', 'lat'])
annual_mean
annual_df = annual_mean.to_dataframe()
annual_df
annual_df.plot()
annual_df['anomaly'] = annual_df['no2'] - annual_df['no2'].mean()
annual_df
annual_df.anomaly.plot.bar()
plt.savefig('anomaly.png', dpi=360, bbox_inches='tight')
annual_df['pct'] = annual_df.no2.pct_change()
annual_df.pct.plot()
monthly = ds.resample(time='M').mean('time')
monthly
monthly_mean = monthly.mean(dim=['lon', 'lat'])
monthly_df = monthly_mean.to_dataframe()
monthly_df
monthly2020 = monthly_df[monthly_df.index.year == 2020]
monthly2020
monthly_df.plot()
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly_df.index, monthly_df.no2)
ax.plot(monthly2020.index, monthly2020.no2)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'air_quality', '0125_covid_air_pollution', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'air_quality')  # explicit upload; requires Drive OAuth scope
