# Bangladesh adaptation: 0133_xee_temp_anomaly
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0133_xee_temp_anomaly'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""0048_temp_anomaly_detection.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-138: Temeprature Anomaly and Extreme Detection in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xee
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
temp = ee.ImageCollection('MODIS/061/MOD11A2').filterDate('2001', '2025').select('LST_Day_1km').map(lambda img: img.multiply(0.02).subtract(273.15).copyProperties(img, img.propertyNames()))
temp
xtemp = xr.open_dataset(temp, engine='ee', crs='EPSG:4326', scale=0.01, geometry=BD_ROI)
xtemp
xtemp_mean = xtemp.mean(dim=['lon', 'lat'])
xtemp_mean.LST_Day_1km.plot()
xtemp_inte = xtemp_mean.interpolate_na(dim='time')
xtemp_df = xtemp_inte.to_dataframe()
xtemp_df.to_csv('temp_df.csv')
from statsmodels.tsa.seasonal import seasonal_decompose
model = seasonal_decompose(xtemp_df, model='additive', period=46)
model.plot()
plt.show()
final_df = pd.DataFrame({'time': model.observed.index, 'observations': model.observed.values, 'trend': model.trend.values, 'seasonal': model.seasonal.values, 'residuals': model.resid.values})
final_df = final_df.set_index('time')
final_df.residuals.plot()
final_df.to_csv('temp_anomaly.csv')
pos = final_df[final_df['residuals'] >= 0]
neg = final_df[final_df['residuals'] < 0]
plt.bar(pos.index, pos.residuals, width=10)
plt.bar(neg.index, neg.residuals, width=10)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0133_xee_temp_anomaly', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
