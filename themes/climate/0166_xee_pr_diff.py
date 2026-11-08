# Bangladesh adaptation: 0166_xee_pr_diff
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0166_xee_pr_diff'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0091_pr_change.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-171: Precipitation Annual Change Detection using Differencing Technique

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
border = BD_ROI
map.addLayer(border, {}, 'border')
gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate('2015', '2025').select('precipitation').map(lambda img: img.clip(border).copyProperties(img, ['system:time_start']))
gpm.getInfo()
import xarray as xr
pr = xr.open_dataset(gpm, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
pr = pr.sortby('time') * 730.001
import numpy as np
pr_annual = pr.resample(time='YE').sum('time')
pr_annual = xr.where(pr_annual == 0, np.nan, pr_annual)
pr_annual.precipitation.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, robust=True, levels=10)
annual_change = pr_annual.diff('time')
import matplotlib.pyplot as plt
annual_change.precipitation.plot.contourf(x='lon', y='lat', col='time', col_wrap=5, robust=True, levels=20)
plt.savefig('pr_change.png', dpi=360, bbox_inches='tight')
mean_change = annual_change.mean(dim='time')
mean_change.precipitation.plot.contourf(x='lon', y='lat', robust=True, levels=10)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0166_xee_pr_diff', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
