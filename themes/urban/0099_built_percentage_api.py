# Bangladesh adaptation: 0099_built_percentage_api
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'urban' / '0099_built_percentage_api'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""
Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-104: Built-up Change Percentage, using Python API

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!
"""
import ee
import geemap as gee
None
None
cor = [[51.08709442761703, 35.52787565438577], [51.67348969128891, 35.52787565438577], [51.67348969128891, 35.88138095518934], [51.08709442761703, 35.88138095518934], [51.08709442761703, 35.52787565438577]]
cor
roi = BD_ROI
roi
map = gee.Map(basemap='SATELLITE')
map.centerObject(roi)
map.addLayer(roi, {}, 'roi')
map
built = ee.ImageCollection('JRC/GHSL/P2023A/GHS_BUILT_S').select('built_surface')
built
stack = built.toBands().clip(roi)
stack
map.addLayer(stack, {}, 'stack')

def ext_area(img):
    thr = img.gt(0)
    mask = thr.updateMask(thr)
    area = mask.multiply(ee.Image.pixelArea())
    val = area.reduceRegion(reducer=ee.Reducer.sum(), geometry=roi, scale=100).values().get(0)
    date = img.date().format('YYYY-MM-dd')
    return ee.Feature(None, {'date': date, 'area': val})
built_area = built.map(ext_area)
built_area
area_list = built_area.toList(built_area.size()).getInfo()
area_list
date = [item['properties']['date'] for item in area_list]
date
area = [item['properties']['area'] for item in area_list]
area
import pandas as pd
import numpy as np
df = pd.DataFrame({'date': date, 'area': area})
df['date'] = pd.to_datetime(df['date'])
df_index = df.set_index('date').divide(1000000.0).round(2)
df_index
df_index.to_csv('built_area_tehran.csv')
df_index.plot()
'change_perce = ((current - previous)/ previous) * 100'
current = df_index.copy()
previous = df_index.shift(1)
previous
change = (current - previous) / previous * 100
change
change.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'urban', '0099_built_percentage_api', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'urban')  # explicit upload; requires Drive OAuth scope
