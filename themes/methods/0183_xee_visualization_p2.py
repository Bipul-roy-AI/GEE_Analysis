# Bangladesh adaptation: 0183_xee_visualization_p2
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0183_xee_visualization_p2'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0108_plotting.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-188: Visualization and Plotting (Part -2)

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
collection = ee.ImageCollection('CSIC/SPEI/2_10').select('SPEI_12_month').filterDate('1990', '2026')
collection
import xarray as xr
ds = xr.open_dataset(collection, engine='ee', geometry=BD_ROI, scale=0.55, crs='EPSG:4326')
ds = ds.sortby('time') * 1
import matplotlib.pyplot as plt
df = ds.SPEI_12_month.to_dataframe().reset_index()[['time', 'SPEI_12_month']].set_index('time')
df.plot()
fig, ax = plt.subplots(figsize=(7, 2))
ax.plot(df.index, df, color='tab:red', lw=1.2, ls='-', label='SPEI')
ax.legend(loc='lower left')
ax.set_title('Drought Monitoring')
ax.grid(alpha=0.5, ls=':')
ax.tick_params(axis='both', direction='in', top=True, right=True)
ax.set_ylabel('SPEI')
ax.set_xlabel('12-Months')
plt.savefig('SPEI.png', bbox_inches='tight', dpi=360)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0183_xee_visualization_p2', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
