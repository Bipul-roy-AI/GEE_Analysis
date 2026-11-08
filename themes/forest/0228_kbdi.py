# Bangladesh adaptation: 0228_kbdi
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'forest' / '0228_kbdi'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00018_kbdi.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-206: Keetch Byram Drought Index (KBDI) in Python
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

# **Connect to GEE**
"""
import ee
None
None
'# **Study Area**'
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_COUNTRY
roi
canada = BD_COUNTRY
map.addLayer(canada, {}, 'canada')
'# **ERA5 Image Collection**'
era5 = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate('2010', '2020').select(['maximum_2m_air_temperature', 'total_precipitation'], ['max_temp', 'pr'])
era5
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_30km = helpers.fit_geometry(geometry=shape(canada.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.3, -0.3))
ds = xr.open_dataset(era5, engine='ee', **grid_30km)
ds = ds.sortby('time') * 1
'# **Data Preparation**'
ds['pr'] = ds['pr'] * 1000
ds['pr'].attrs['units'] = 'mm/day'
ds_annual = ds['pr'].resample(time='YE').sum('time')
ds_annual = ds_annual.mean(dim='time')
ds_annual.attrs['units'] = 'mm/year'
ds_annual
ds['max_temp'] = ds['max_temp'] - 273.15
ds['max_temp'].attrs['units'] = 'degC'
ds
import rioxarray
import geopandas as gpd
canada_gdf = geemap.ee_to_gdf(ee.FeatureCollection(canada))
ds_clip = ds.rio.clip(canada_gdf.geometry, canada_gdf.crs)
pr_annual_clip = ds_annual.rio.clip(canada_gdf.geometry, canada_gdf.crs)
'# **KBDI**'
import xclim.indicators.atmos as xindex
help(xindex.keetch_byram_drought_index)
kbdi = xindex.keetch_byram_drought_index(pr=ds_clip['pr'], tasmax=ds_clip['max_temp'], pr_annual=pr_annual_clip)
kbdi_mean = kbdi.max(dim='time')
kbdi_mean.plot.contourf(x='x', y='y', robust=True, figsize=(12, 5), cmap='turbo', levels=10)
kbdi.sel(x=-120.776171875, y=51.63486105108019, method='nearest').to_dataframe()['kbdi'].plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0228_kbdi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
