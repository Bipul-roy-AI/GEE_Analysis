/* Headless planner for the supplied tutorials. It never submits an EE task.
 * Uses the official EE JS SDK; chart data are exported, not UI screenshots.
 * Access token stays in the child environment, never in logs or plan files.
 */
const fs = require('fs');
const vm = require('vm');
const ee = require('@google/earthengine');
const [sourcePath, outputPath] = process.argv.slice(2);
const tasks = [];
function pack(value) {
  if (value instanceof ee.ComputedObject) return {__bdgee_expression__:ee.Serializer.toJSON(value)};
  if (Array.isArray(value)) return value.map(pack);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).filter(([,v])=>v!==undefined).map(([k,v])=>[k,pack(v)]));
  return value;
}
function chart() {
  const chain = new Proxy(function(){return chain;}, {get:(_, key)=>key==='then'?undefined:chain});
  return chain;
}
function capture(type, options) {
  tasks.push({type,raw_options:true,config:pack(options)});
  return {start(){throw Error('Task submission is forbidden inside a planning worker');}};
}
function execute() {
  // Also disable SDK-native batch submission if a source tries to bypass Export.
  ee.data.startProcessing = ()=>{throw Error('Task submission is forbidden inside a planning worker');};
  const context={ee,console,Map:{addLayer(){},centerObject(){},setOptions(){}},
    Export:{image:{toDrive:options=>capture('EXPORT_IMAGE',options)},table:{toDrive:options=>capture('EXPORT_TABLE',options)}},
    print(...values) {
      for (const value of values) {
        if (value instanceof ee.List || value instanceof ee.Array || value instanceof ee.String) {
          capture('EXPORT_TABLE',{collection:ee.FeatureCollection([ee.Feature(null,{value:value instanceof ee.Array?value.toList():value})]),description:'console_data_'+tasks.length,folder:'BD_GEE_methods',fileFormat:'CSV'});
        } else if (value instanceof ee.FeatureCollection) {
          capture('EXPORT_TABLE',{collection:value,description:'console_features_'+tasks.length,folder:'BD_GEE_methods',fileFormat:'GeoJSON'});
        }
      }
    },ui:{Chart:{image:{series:chart,histogram:chart,seriesByRegion:chart,
      byClass(image,classBand,region,reducer,scale) {
        const group=image.bandNames().indexOf(classBand);
        const values=image.reduceRegion({reducer:reducer.group({groupField:group,groupName:'class'}),geometry:region,scale:scale,maxPixels:1e13,tileScale:4});
        capture('EXPORT_TABLE',{collection:ee.FeatureCollection([ee.Feature(null,values)]),description:'class_statistics_'+tasks.length,folder:'BD_GEE_methods',fileFormat:'CSV'});
        return chart();
      },
      doySeriesByYear(collection,band,region,reducer,scale) {
        const rows=ee.ImageCollection(collection).select(band).toList(ee.ImageCollection(collection).size()).map(item=>{
          const image=ee.Image(item);
          return ee.Feature(null,image.reduceRegion({reducer,geometry:region,scale,maxPixels:1e13,tileScale:4}))
            .set('date',image.date().format('YYYY-MM-dd')).set('year',image.date().get('year')).set('day_of_year',image.date().getRelative('day','year').add(1));
        });
        capture('EXPORT_TABLE',{collection:ee.FeatureCollection(rows),description:'day_of_year_values_'+tasks.length,folder:'BD_GEE_methods',fileFormat:'CSV'});
        return chart();
      }}}}};
  let code=fs.readFileSync(sourcePath,'utf8').replace('var BD_CREATE_EXPORTS = false;', 'var BD_CREATE_EXPORTS = true;');
  // Existing source scales are retained; displayed maps use the header's explicit
  // review scale. Do not manufacture training features or substitute algorithms.
  vm.runInNewContext(code,context,{filename:sourcePath});
  if (!tasks.length) throw Error('Source produced no exportable outputs');
  fs.writeFileSync(outputPath,JSON.stringify({tasks,local_files:[]},null,2));
}
if (process.env.BDGEE_OFFLINE_ALGORITHMS) {
  // Tests only: official SDK signatures, no imagery or remote computation.
  const algorithms=JSON.parse(fs.readFileSync(process.env.BDGEE_OFFLINE_ALGORITHMS,'utf8'));
  ee.data.getAlgorithms=callback=>callback?callback(algorithms):algorithms;
  ee.initialize(null,null,execute,error=>{console.error(String(error));process.exitCode=1;},null,'axial-paratext-491911-b6');
} else {
  if (!process.env.BDGEE_ACCESS_TOKEN) throw Error('Missing in-memory Earth Engine access token');
  ee.data.setAuthToken('','Bearer',process.env.BDGEE_ACCESS_TOKEN,3600,[],undefined,false);
  ee.initialize(null,null,execute,error=>{console.error(String(error));process.exitCode=1;},null,'axial-paratext-491911-b6');
}
