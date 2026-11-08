// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'terrain';
var BD_SOURCE = '00067_aster_lithology';
var BD_FOLDER = 'BD_GEE_' + BD_THEME;
var BD_SCALE = 1000; // EDIT to native analysis resolution; 1000 is a review default.
var BD_CREATE_EXPORTS = false; // Set true AFTER reviewing science, units and task volume.
var BD_COUNTRY = ee.FeatureCollection('FAO/GAUL/2015/level0')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var BD_DISTRICTS = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var BD_ROI = BD_COUNTRY.geometry();
// Aliases also replace missing drawn/imported study-area variables, not training labels.
var roi = BD_ROI, geometry = BD_ROI, table = BD_COUNTRY;
var coordinates = BD_ROI.coordinates();
var BD_serial = 0;
function BD_name(text) {
  BD_serial += 1;
  return (BD_SOURCE + '_' + BD_serial + '_' + text).replace(/[^A-Za-z0-9_-]/g, '_').slice(0, 95);
}
var BD_imageExport = Export.image.toDrive;
var BD_tableExport = Export.table.toDrive;
// Route existing exports to the national boundary and theme folder.
Export.image.toDrive = function(options) {
  if (!BD_CREATE_EXPORTS) { print('Export disabled; review BD_CREATE_EXPORTS', options.description); return; }
  options.folder = BD_FOLDER;
  options.description = BD_name(options.description || 'raster');
  options.fileNamePrefix = options.description;
  options.region = BD_ROI;
  options.image = ee.Image(options.image).clip(BD_ROI).toFloat();
  options.maxPixels = 1e13;
  return BD_imageExport(options);
};
Export.table.toDrive = function(options) {
  if (!BD_CREATE_EXPORTS) { print('Export disabled; review BD_CREATE_EXPORTS', options.description); return; }
  options.folder = BD_FOLDER;
  options.description = BD_name(options.description || 'table');
  options.fileNamePrefix = options.description;
  return BD_tableExport(options);
};
// Every displayed EE raster gets a raw GeoTIFF and regional descriptive table.
// For categorical products use the national toolkit's class-area workflow instead
// of interpreting this generic descriptive table as a class statistic.
var BD_addLayer = Map.addLayer;
Map.addLayer = function(object, vis, name, shown, opacity) {
  var result = BD_addLayer(object, vis, name, shown, opacity);
  if (BD_CREATE_EXPORTS && object instanceof ee.Image) {
    var image = ee.Image(object).clip(BD_ROI);
    Export.image.toDrive({image:image, description:name || 'map', region:BD_ROI,
      scale:BD_SCALE, crs:'EPSG:6933', fileFormat:'GeoTIFF',
      formatOptions:{cloudOptimized:true}});
    var stats = image.reduceRegions({collection:BD_DISTRICTS.merge(BD_COUNTRY),
      reducer:ee.Reducer.mean().combine({reducer2:ee.Reducer.minMax(), sharedInputs:true})
        .combine({reducer2:ee.Reducer.count(), sharedInputs:true}),
      scale:BD_SCALE, crs:'EPSG:6933', tileScale:4})
      .map(function(f){return f.setGeometry(null).set('source',BD_SOURCE);});
    Export.table.toDrive({collection:stats, description:(name || 'map')+'_descriptive_stats', fileFormat:'CSV'});
  }
  return result;
};
// Export the values underlying image-series charts, not a screenshot of a chart.
var BD_series = ui.Chart.image.series;
ui.Chart.image.series = function(collection, region, reducer, scale, xProperty) {
  var originalArgs=Array.prototype.slice.call(arguments);
  if (collection && collection.imageCollection) {
    var opts=collection; collection=opts.imageCollection; region=opts.region;
    reducer=opts.reducer;scale=opts.scale;xProperty=opts.xProperty;
  }
  if (BD_CREATE_EXPORTS) {
    var rows = ee.ImageCollection(collection).toList(ee.ImageCollection(collection).size()).map(function(item) {
      var image = ee.Image(item);
      var values = image.reduceRegion({reducer:reducer || ee.Reducer.mean(),
        geometry:BD_ROI, scale:scale || BD_SCALE, maxPixels:1e13,tileScale:4});
      return ee.Feature(null,values).set('time_start',image.get(xProperty || 'system:time_start'));
    });
    Export.table.toDrive({collection:ee.FeatureCollection(rows),description:'chart_values',fileFormat:'CSV'});
  }
  return BD_series.apply(null,originalArgs);
};
Map.centerObject(BD_ROI,7);
// Preserve printed scalar/dictionary results as CSV as well as Console output.
var BD_print = print;
print = function() {
  for (var j = 0; j < arguments.length; j++) {
    var value = arguments[j];
    if (BD_CREATE_EXPORTS && (value instanceof ee.Number || value instanceof ee.Dictionary)) {
      var props = value instanceof ee.Dictionary ? value : ee.Dictionary({value:value});
      BD_tableExport({collection:ee.FeatureCollection([ee.Feature(null,props)]),
        description:BD_name('console_value'), folder:BD_FOLDER, fileFormat:'CSV'});
    }
  }
  return BD_print.apply(null,arguments);
};
var BD_histogram = ui.Chart.image.histogram;
ui.Chart.image.histogram = function(image, region, scale, maxBuckets, minBucketWidth, maxRaw) {
  var originalArgs=Array.prototype.slice.call(arguments);
  if (image && image.image) {
    var opts=image;image=opts.image;region=opts.region;scale=opts.scale;maxBuckets=opts.maxBuckets;
  }
  if (BD_CREATE_EXPORTS) {
    var histogram = ee.Image(image).reduceRegion({reducer:ee.Reducer.autoHistogram(maxBuckets || 128),
      geometry:BD_ROI,scale:scale || BD_SCALE,maxPixels:1e13,tileScale:4});
    Export.table.toDrive({collection:ee.FeatureCollection([ee.Feature(null,histogram)]),
      description:'histogram_bucket_values_counts',fileFormat:'CSV'});
  }
  return BD_histogram.apply(null,originalArgs);
};
var BD_seriesByRegion = ui.Chart.image.seriesByRegion;
ui.Chart.image.seriesByRegion = function(collection, regions, reducer, band, scale, xProperty, seriesProperty) {
  var originalArgs=Array.prototype.slice.call(arguments);
  if (collection && collection.imageCollection) {
    var opts=collection;collection=opts.imageCollection;regions=opts.regions;
    reducer=opts.reducer;band=opts.band;scale=opts.scale;xProperty=opts.xProperty;seriesProperty=opts.seriesProperty;
  }
  if (BD_CREATE_EXPORTS) {
    var rows = ee.ImageCollection(collection).toList(ee.ImageCollection(collection).size()).map(function(item) {
      var image=ee.Image(item);
      if (band) image=image.select(band);
      return image.reduceRegions({collection:BD_DISTRICTS,reducer:reducer || ee.Reducer.mean(),
        scale:scale || BD_SCALE,tileScale:4}).map(function(f){
          return f.setGeometry(null).set('time_start',image.get(xProperty || 'system:time_start'));
        });
    });
    Export.table.toDrive({collection:ee.FeatureCollection(rows).flatten(),description:'series_by_district',fileFormat:'CSV'});
  }
  return BD_seriesByRegion.apply(null,originalArgs);
};



/*
Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!
*/ 

var cor  = [
  [51.593180412962234,33.80432620586323],
  [54.295817131712234,33.80432620586323],
  [54.295817131712234,35.104250404611456],
  [51.593180412962234,35.104250404611456],
  [51.593180412962234,33.80432620586323]
  ]

var geometry = BD_ROI

Map.centerObject(geometry)

var aster = ee.ImageCollection("ASTER/AST_L1T_003")
.filterBounds(geometry)
.filter(ee.Filter.lt('CLOUDCOVER',10))
.filter(ee.Filter.calendarRange(6, 9, 'month'))
.mean()

print(aster)

Map.addLayer(aster.clip(geometry),[],'aster',false)

function dos(img){
  
  
  var ms = img.select('B0[1-9]', 'B3N');
  var tir = img.select('B1[0-4]');
  
  var dark_object = ms.reduceRegion({
    reducer: ee.Reducer.min(), geometry: geometry, scale: 500
    });
  
  
  var bands = ms.bandNames()
  
  var cor = bands.map(function(band_name){
    var do_val = ee.Number(dark_object.get(band_name))
    var cor = ms.select([band_name]).subtract(do_val)
    return cor
    });
    
    
  return ee.ImageCollection(cor).toBands().addBands(tir)
  
  }
  
var aster_cor = dos(aster);

print(aster_cor.bandNames())

function lithology(img, index){
  
  var kli = img.expression('(b4/b5)*(b8/b6)',
  {'b4': img.select('2_B04'), 'b5': img.select('3_B05'), 'b6': img.select('4_B06'), 'b8': img.select('6_B08')}).rename('kaolinite')
  
  var ali = img.expression('(b7/b5)*(b7/b8)',
  {'b5': img.select('3_B05'), 'b7': img.select('5_B07'), 'b8': img.select('6_B08')}).rename('alunite')
  
  var cli = img.expression('(b6/b8)*(b9/b8)',
  {'b6': img.select('4_B06'), 'b8': img.select('6_B08'), 'b9': img.select('7_B09')}).rename('calcite')
  
  var qi = img.expression('(b11 * b11)/(b10 * b12)', 
  {'b10': img.select('B10'), 'b11': img.select('B11'), 'b12': img.select('B12')}).rename('quartz')
  
  var ci = img.expression('b13/b14', 
  {'b13': img.select('B13'), 'b14': img.select('B14')}).rename('carbonate')
  
  var mi = img.expression('b12/b13', 
  {'b12': img.select('B12'), 'b13': img.select('B13')}).rename('mafic')
  
  return ee.Image(ee.Algorithms.If(index === 'kaolinite', kli, 
  ee.Algorithms.If(index === 'alunite', ali, 
  ee.Algorithms.If(index === 'calcite', cli, 
  ee.Algorithms.If(index === 'quartz', qi, 
  ee.Algorithms.If(index === 'carbonate', ci, 
  ee.Algorithms.If(index === 'mafic', mi)))))))
  
  }

var kaolinite = lithology(aster_cor, 'kaolinite')
var alunite = lithology(aster_cor, 'alunite')
var calcite = lithology(aster_cor, 'calcite')
var quartz = lithology(aster_cor, 'quartz')
var carbonate = lithology(aster_cor, 'carbonate')
var mafic = lithology(aster_cor, 'mafic')



Map.addLayer(kaolinite.clip(geometry), [], 'kaolinite', false)
Map.addLayer(alunite.clip(geometry), [], 'alunite', false)
Map.addLayer(calcite.clip(geometry), [], 'calcite', false)
Map.addLayer(quartz.clip(geometry), [], 'quartz', false)
Map.addLayer(carbonate.clip(geometry), [], 'carbonate', false)
Map.addLayer(mafic.clip(geometry), [], 'mafic', false)

Map.addLayer(kaolinite.addBands(calcite).addBands(quartz).clip(geometry),[],'kao+cal+qua',false)
