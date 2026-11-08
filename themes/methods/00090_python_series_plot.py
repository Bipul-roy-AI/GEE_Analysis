# Bangladesh adaptation: 00090_python_series_plot
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '00090_python_series_plot'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0005_temperature_plot3.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-95: Time Series Plot using Google Colab

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!

"""
import ee
import geemap as gee
None
None
temp = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate('2022', '2024').select('temperature_2m')
temp
map = gee.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi

def temp_val(img):
    date = img.date().format('YYYY-MM-dd')
    temp_mean = img.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi, scale=10000).values().get(0)
    return ee.Feature(None, {'date': date, 'temp': temp_mean})
features = temp.map(temp_val)
features
data_list = features.toList(features.size()).getInfo()
data_list
date = [item['properties']['date'] for item in data_list]
temp_list = [item['properties']['temp'] for item in data_list]
temp_list
import pandas as pd
df = pd.DataFrame({'date': date, 'temp': temp_list}).round(2)
df
df.to_csv('temp_2022-2023.csv')
df['date'] = pd.to_datetime(df['date'])
import matplotlib.pyplot as plt
plt.plot(df['date'], df['temp'], lw=2, ls='--', color='red', marker='o')
plt.title('temperature')
plt.ylabel('K$^o$')
plt.savefig('temp_fig.png', dpi=360)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '00090_python_series_plot', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
