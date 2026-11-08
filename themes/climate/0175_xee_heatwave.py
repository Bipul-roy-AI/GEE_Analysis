# Bangladesh adaptation: 0175_xee_heatwave
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0175_xee_heatwave'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0098_heatwave.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-180: Heatwave Mapping and Monitoring using Xee

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
era5 = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate('2010', '2020').select(['maximum_2m_air_temperature'], ['tmax'])
era5
import xarray as xr
ds = xr.open_dataset(era5, engine='ee', crs='EPSG:4326', scale=0.3, geometry=BD_ROI)
ds = ds.sortby('time') - 273.15
tmax = ds.tmax
tmax.attrs['units'] = 'degC'
tmax
from xclim.indicators.atmos import heat_wave_index
hw = heat_wave_index(tasmax=ds.tmax, thresh='25 degC', window=5, freq='YS')
import matplotlib.pyplot as plt
hw.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, cmap='turbo', levels=15)
plt.savefig('hw_index.png', dpi=360, bbox_inches='tight')
point = hw.sel(lat=46.90484567845552, lon=2.872345969440646, method='nearest')
df = point.to_dataframe().heat_wave_index
df
fig, ax = plt.subplots(figsize=(8, 2))
ax.plot(df.index, df, marker='o', color='red', ls='--')
ax.set_ylabel('Heat Wave Days')
ax.grid(ls=':', alpha=0.5)
ax.set_title('Location:' + ' lat:2.87' + ' lon:46.90')
ax.tick_params(axis='both', direction='in', top=True, right=True)
plt.savefig('hw_plot.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0175_xee_heatwave', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
