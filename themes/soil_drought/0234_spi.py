# Bangladesh adaptation: 0234_spi
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0234_spi'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00023_spi.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-210: Standardized Precipitation Index, SPI
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
'# **Precipitation Image Collection**'
gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate('2000', '2025').select('precipitation')
gpm
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_10km = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.1, -0.1))
ds = xr.open_dataset(gpm, engine='ee', **grid_10km)
ds = ds.sortby('time') * 1
'# **SPI**'
import xclim.indicators.atmos as xatmos
ds['precipitation'].attrs['units'] = 'mm/hour'
ds
help(xatmos.standardized_precipitation_index)
spi = xatmos.standardized_precipitation_index(pr=ds['precipitation'], window=6)
spi_mean = spi.mean(dim=['x', 'y'])
spi_df2 = spi_mean.to_dataframe()
spi_df2.plot()
spi_df = spi_mean.to_dataframe()
spi_df.to_csv('spi_excel_format.csv')
spi_df.plot()
'# **Visualization**'
wet_months = spi_df[spi_df.spi >= 0]
dry_months = spi_df[spi_df.spi < 0]
dry_months
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 3))
ax.bar(wet_months.index, wet_months.spi, color='tab:blue', width=40, label='wet months')
ax.bar(dry_months.index, dry_months.spi, color='tab:red', width=40, label='dry months')
ax.plot(spi_df.index, spi_df.spi, color='black')
ax.legend()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0234_spi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
