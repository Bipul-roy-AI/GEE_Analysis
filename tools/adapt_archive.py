"""Rebuild all Bangladesh tutorial adaptations from the supplied archive.
Source code is treated as data, never executed by this importer.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import zipfile
import sys
import esprima
import nbformat as nb

ROOT=Path(__file__).resolve().parents[1]


def classify(name,source):
    n=name.lower()
    if re.search(r'lst|tsharp',n):return 'urban'
    if re.search(r'era5|utci',n):return 'climate'
    if 'andwi' in n:return 'water'
    if 'sm_downscale' in n:return 'soil_drought'
    if name.startswith('0197_'):return 'landcover'
    if re.search(r'bootcamp|session', n):
        title=re.search(r'Tutorial Video:([^\n]+)', source)
        if title:n += ' '+title.group(1).lower()
    groups=[('snow',r'snow|frost|cold_spell|ice_cover'),
      ('water_quality',r'turbidity|chlorophyll|chl_water|cyanobacteria|cdom|tss|ocean|salinity|water_temperature|oil_spill'),
      ('flood',r'flood|heavy_pr_valencia'),('forest',r'forest|hansen|tree_cover|carbon|biomass|canopy|wildfire|wildefire|dnbr|python_nbr|kbdi'),
      ('agriculture',r'crop|irrigat|npp_crop|growing_season|phenology'),
      ('air_quality',r'sen5|sulfure|dust|pm25|air_pollution|airquality|methane'),
      ('urban',r'urban|built|night_light|uhi|green_space'),('population',r'pop'),
      ('terrain',r'terrain|dem|lithology|subsidence'),
      ('soil_drought',r'soil|optram|totram|sartram|vci|vhi|spei|spi|ssmi|drought|esi|aridity|water_deficit|cwsi|et_model|et_cwsi|evaporation|water_consumption|grace|ground_water|water_storage|veg_opt_depth|et_modelling'),
      ('water',r'lake|water|coast|shore|river|wetland|otsu'),
      ('climate',r'pr_|precipitation|rainfall|temperature|temp|wind|dry_wet|dry_spell|heatwave|climate|cold_spell'),
      ('landcover',r'landcover|land_cover|class_area|dynamic_world|embedding|similarity|change_detection'),
      ('vegetation',r'ndvi|lai|veg|svi|smoothing|sg_filter')]
    for theme,pattern in groups:
        if re.search(pattern,n):return theme
    return 'methods'

GEO_NAMES=set('roi geometry geometry2 geometry3 roi1 roi2 roi3 border iran tehran province loc point point1 point2 point3 point_algeria point_iran training_border training_geometry coordinates'.split())


class AdaptPython(ast.NodeTransformer):
    def visit_Assign(self,node):
        text=ast.unparse(node.value)
        names=[t.id for t in node.targets if isinstance(t,ast.Name)]
        if any(n in ('bbox',) for n in names):node.value=ast.parse('BD_BBOX',mode='eval').body
        elif any(n in GEO_NAMES for n in names) and any(t in text for t in ['ee.Geometry','ee.FeatureCollection','draw_last_feature','filterBounds','geometry()']):
            node.value=ast.parse('BD_COUNTRY' if ('filterBounds' in text or 'ee.FeatureCollection' in text) and '.geometry(' not in text and 'ee.Geometry' not in text and 'draw_last_feature' not in text else 'BD_ROI',mode='eval').body
        elif 'ee.FeatureCollection' in text and any(t in text for t in ['GAUL','LSIB','HydroSHEDS','HydroATLAS']):
            node.value=ast.parse('BD_COUNTRY',mode='eval').body
        node=self.generic_visit(node)
        if names==['ds_clean'] and 'stackstac' in getattr(self,'source',''):
            return [node, ast.parse("import rioxarray\nds_clean = ds_clean.rio.write_crs('EPSG:3857').rio.clip([BD_ROI.getInfo()], crs='EPSG:4326')").body[0], ast.parse("ds_clean = ds_clean.rio.write_crs('EPSG:3857').rio.clip([BD_ROI.getInfo()], crs='EPSG:4326')").body[0]]
        return node
    def visit_Call(self,node):
        target=ast.unparse(node.func)
        if target in ('ee.Initialize','ee.Authenticate'):
            return ast.copy_location(ast.Constant(None),node)
        if target.endswith('ee.Geometry.Point') or target.endswith('ee.Geometry.Polygon') or target.endswith('ee.Geometry.Rectangle'):
            return ast.copy_location(ast.Name(id='BD_ROI',ctx=ast.Load()),node)
        if target in ('xr.open_dataset','xarray.open_dataset'):
            for k in node.keywords:
                if k.arg=='geometry':k.value=ast.Name(id='BD_ROI',ctx=ast.Load())
            if any(k.arg=='engine' and isinstance(k.value,ast.Constant) and k.value.value=='ee' for k in node.keywords) and not any(k.arg=='geometry' or k.arg is None for k in node.keywords):
                node.keywords.append(ast.keyword(arg='geometry',value=ast.Name(id='BD_ROI',ctx=ast.Load())))
        return self.generic_visit(node)


def py_adapt(source):
    source=re.sub(r'/\*(.*?)\*/', lambda m: '"""'+m.group(1)+'"""', source, flags=re.S)
    source=source.replace(".drop_dims('band')", '').replace('.drop_dims("band")', '')
    source=re.sub(r'^ (import |!pip)', r'\1', source, flags=re.M)
    cleaned='\n'.join('# Notebook installer removed: '+l if l.lstrip().startswith(('!','%')) else l for l in source.splitlines())
    tree=ast.parse(cleaned.lstrip())
    # Keep original docstrings (attribution); AST formatter removes only comments.
    adapter=AdaptPython()
    adapter.source=source
    tree=adapter.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)+'\n'


def js_adapt(source):
    tree=esprima.parseScript(source,{'range':True,'tolerant':True})
    edits=[]
    for stmt in tree.body:
        if stmt.type!='VariableDeclaration':continue
        for dec in stmt.declarations:
            if not dec.init or dec.id.type!='Identifier':continue
            name=dec.id.name
            text=source[dec.init.range[0]:dec.init.range[1]]
            replacement=None
            if name in GEO_NAMES and any(s in text for s in ['ee.Geometry','ee.FeatureCollection','filterBounds','geometry()']):replacement='BD_COUNTRY' if ('filterBounds' in text or 'ee.FeatureCollection' in text) and '.geometry(' not in text and 'ee.Geometry' not in text else 'BD_ROI'
            elif 'ee.FeatureCollection' in text and any(s in text for s in ['GAUL','LSIB','HydroSHEDS','HydroATLAS']):replacement='BD_COUNTRY'
            if replacement:edits.append((*dec.init.range,replacement))
    for a,b,s in sorted(edits,reverse=True):source=source[:a]+s+source[b:]
    # Remove all remaining explicit foreign literal geometries including helper sites.
    tree=esprima.parseScript(source,{'range':True,'tolerant':True})
    edits=[]
    def walk(node):
        if not hasattr(node,'type'):return
        if node.type=='CallExpression':
            text=source[node.callee.range[0]:node.callee.range[1]]
            if text in ('ee.Geometry.Point','ee.Geometry.Polygon','ee.Geometry.Rectangle'):
                edits.append((*node.range,'BD_ROI'));return
        for v in vars(node).values():
            if isinstance(v,list):
                for x in v:walk(x)
            elif hasattr(v,'type'):walk(v)
    walk(tree)
    for a,b,s in sorted(edits,reverse=True):source=source[:a]+s+source[b:]
    return source


def main(archive):
    manifest=[]
    previous=ROOT/'catalog.json'
    if previous.exists():
        for item in json.loads(previous.read_text()):
            old=ROOT/item['adapted']
            if old.is_relative_to(ROOT/'themes'):
                old.unlink(missing_ok=True)
                if old.suffix=='.py':old.with_suffix('.ipynb').unlink(missing_ok=True)
    z=zipfile.ZipFile(archive)
    for entry in sorted(z.infolist(),key=lambda e:e.filename):
        if entry.is_dir():continue
        name=Path(entry.filename).name
        raw=z.read(entry);source=raw.decode('utf-8-sig')
        theme=classify(name,source)
        original=ROOT/'originals'/name
        original.parent.mkdir(exist_ok=True);original.write_bytes(raw)
        out=ROOT/'themes'/theme
        out.mkdir(parents=True,exist_ok=True)
        language='python' if re.search(r'^import (ee|xarray)', source, re.M) or source.lstrip().startswith(('#','{')) else 'javascript'
        if source.lstrip().startswith('{'):
            book=json.loads(source)
            source='\n\n'.join(''.join(c['source']) for c in book['cells'] if c['cell_type']=='code')
        notes=['Static adaptation only; Earth Engine/data/asset execution not verified.',
               'Original scientific assumptions and date windows retained; use the national workflow for QA improvements.',
               'Review scale, missing data, units, and any training/calibration requirements before interpreting results.']
        if theme=='snow':notes.append('Bangladesh has no persistent seasonal snowpack; valid no-snow results are expected. Cloud/no-data is not snow-free.')
        if theme=='water_quality':notes.append('Water-quality ratios are proxies without local calibration. National land boundary excludes offshore sea; no maritime claim is implied.')
        if re.search(r'train\(|\.fit\(|downscal|sharpen',source,re.I):notes.append('Experimental model: use spatial/time holdout validation and independent Bangladesh ground truth; finer pixels do not prove added information.')
        if re.search(r'projects/|users/|table\b|geometry\b',source):notes.append('May contain tutorial-specific assets or imported training features; inspect dependencies before execution.')
        try:
            if language=='python':
                adapted=py_adapt(source)
                header=f'''# Bangladesh adaptation: {name}\n# Original author: Amirhossein Ahrari; see original attribution below and originals/.\nfrom bdgee.core import initialize, boundaries\nfrom bdgee.notebook import export_outputs, upload_local\ninitialize()  # Run `earthengine authenticate` first; project is configured in bdgee.\nBD_COUNTRY, BD_DISTRICTS = boundaries()\nBD_ROI = BD_COUNTRY.geometry()\nBD_BBOX = [88.0, 20.5, 92.7, 26.7]  # search only, not analysis boundary\nroi = geometry = border = iran = tehran = province = loc = point = BD_ROI\n# Run from the repository root; all local outputs are isolated by source.\nfrom pathlib import Path\nimport os\n_REPO_ROOT = Path.cwd()\n_OUTPUT_DIR = _REPO_ROOT / 'outputs' / '{theme}' / '{name}'\n_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)\nos.chdir(_OUTPUT_DIR)\n'''
                footer=f'''\n# Review these task plans; task creation does not start exports.\nos.chdir(_REPO_ROOT)\nbd_tasks = export_outputs(globals(), '{theme}', '{name}', scale=1000)\n# Set an appropriate native scale above before creating plans.\n# for task in bd_tasks: task.start()\n# upload_local(_OUTPUT_DIR, '{theme}')  # explicit upload; requires Drive OAuth scope\n'''
                script=header+adapted+footer
                target=out/(name.removesuffix('.py')+'.py')
                target.write_text(script)
                notebook=nb.v4.new_notebook(cells=[nb.v4.new_markdown_cell('# Bangladesh: '+name+'\n\n'+'\n\n'.join(notes)),nb.v4.new_code_cell(header),nb.v4.new_code_cell(adapted),nb.v4.new_code_cell(footer)])
                nb.write(notebook,str(target.with_suffix('.ipynb')))
                ast.parse(script)
            else:
                adapted=js_adapt(source)
                header=(ROOT/'tools/js_header.txt').read_text().replace('__THEME__',theme).replace('__SOURCE__',name)
                target=out/(name+'.js')
                target.write_text(header+'\n'+adapted)
                esprima.parseScript(target.read_text())
            status='adapted_unverified'
        except Exception as exc:
            # Never silently lose a source file on conversion failure.
            status='conversion_failed';notes.append(str(exc));target=original
        manifest.append({'source':name,'sha256':hashlib.sha256(raw).hexdigest(),'theme':theme,'language':language,'adapted':str(target.relative_to(ROOT)),'status':status,'datasets':sorted(set(re.findall(r'ee\.(?:ImageCollection|Image|FeatureCollection)\([\"\']([^\"\']+)',source))), 'notes':notes})
    (ROOT/'catalog.json').write_text(json.dumps(manifest,indent=2))
    rows=['# Source-by-source catalogue','', 'Every original file is preserved byte-for-byte in `originals/`. Adaptations retain the tutorial method, with the Bangladesh boundary and themed export helpers. **Unverified means not remotely executed.**','', '| Source | Theme | Adapted file | Status |','|---|---|---|---|']
    for m in manifest:rows.append(f"| {m['source']} | {m['theme']} | [{Path(m['adapted']).name}](../{m['adapted']}) | {m['status']} |")
    (ROOT/'docs/CATALOG.md').write_text('\n'.join(rows)+'\n')
    print(len(manifest),'files;',sum(m['status']=='conversion_failed' for m in manifest),'conversion failures')


if __name__=='__main__':main(sys.argv[1])
