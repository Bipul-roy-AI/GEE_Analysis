# Bangladesh adaptation: 00091_python_mann_kendall
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '00091_python_mann_kendall'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0006_mannkendall_trend_analysis.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-96: Mann-Kendall Trend in GEE

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!

"""
import ee
import geemap as gee
None
None
cor = [24.163332459274812, 62.95500172226916]
roi = BD_ROI
roi
era = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').select('temperature_2m').filterDate('1970', '2024')
era
temp = era.map(lambda img: img.subtract(273.15).copyProperties(img, ['system:time_start']))
temp

def ext_val(img):
    temp_val = img.reduceRegion(reducer=ee.Reducer.first(), geometry=roi, scale=10000).values().get(0)
    date_val = img.date().format('YYYY-MM-dd')
    return ee.Feature(None, {'date': date_val, 'temp': temp_val})
temp_date_val = temp.map(ext_val)
temp_date_val
data_list = temp_date_val.toList(temp_date_val.size()).getInfo()
data_list
temp_list = [item['properties']['temp'] for item in data_list]
date_list = [item['properties']['date'] for item in data_list]
date_list
import pandas as pd
df = pd.DataFrame({'date': date_list, 'temp': temp_list}).round(2)
df
df.to_csv('temp_dataset.csv')
df['date'] = pd.to_datetime(df['date'])
df_annual = df.resample('YE', on='date').mean().round(2)
df_annual
from matplotlib import pyplot as plt
df_annual['temp'].plot(kind='line', figsize=(8, 4), title='temp')
plt.gca().spines[['top', 'right']].set_visible(False)
import pymannkendall as mk
mk_test = mk.original_test(df_annual)
mk_test
import pyhomogeneity as ph
pet_test = ph.pettitt_test(df_annual)
pet_test

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '00091_python_mann_kendall', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
