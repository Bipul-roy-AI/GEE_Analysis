// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'soil_drought';
var BD_SOURCE = '00017_vci_drought_mapping';
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
      scale:BD_SCALE, crs:'EPSG:4326', fileFormat:'GeoTIFF',
      formatOptions:{cloudOptimized:true}});
    var stats = image.reduceRegions({collection:BD_DISTRICTS.merge(BD_COUNTRY),
      reducer:ee.Reducer.mean().combine({reducer2:ee.Reducer.minMax(), sharedInputs:true})
        .combine({reducer2:ee.Reducer.count(), sharedInputs:true}),
      scale:BD_SCALE, crs:'EPSG:4326', tileScale:4})
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

var cor = [52.91994991092,33.56756085477778]

var point = BD_ROI

var feature = BD_COUNTRY

var roi = BD_COUNTRY;

Map.centerObject(roi)
Map.addLayer(roi)

// define start and end time

var time_start = '2001', time_end = '2003'

// call modis ndvi images 

var ndvi = ee.ImageCollection("MODIS/061/MOD13A2")
.select(['NDVI'])
.filterDate(time_start, time_end);

// clculate the vci
// vegetation condition index
// vci = ((ndvi - min)/(max - min)) * 100

var ndvi_min = ndvi.min().multiply(0.0001);
var ndvi_max = ndvi.max().multiply(0.0001);

var vci = ndvi.map(function(img){
  var band = img.multiply(0.0001);
  var index = band.expression('((ndvi - min)/(max - min))*100.0',{
    'ndvi': band, 'min': ndvi_min, 'max': ndvi_max
    }).rename('vci');
  return index
  .copyProperties(img, ['system:time_start','system:time_end'])
  });
  
// drought mapping using vci

var vci_median = vci.median();

Map.addLayer(vci_median.clip(roi),[],'vci_median',false)

// histogram

print(
  ui.Chart.image.histogram(vci_median, roi, 1000)
  )

// vci classification

// making a constant image 

var cons = ee.Image.constant(0);

// define classes

var extreme = cons.where(vci_median.gte(0).and(vci_median.lt(10)), 1);
var severe = extreme.where(vci_median.gte(10).and(vci_median.lt(20)), 2);
var moderate = severe.where(vci_median.gte(20).and(vci_median.lt(30)), 3);
var light = moderate.where(vci_median.gte(30).and(vci_median.lt(40)), 4);
var no1 = light.where(vci_median.gte(40).and(vci_median.lt(60)), 5);
var no2 = no1.where(vci_median.gte(60).and(vci_median.lt(80)), 6);
var no3 = no2.where(vci_median.gte(80), 7);

Map.addLayer(moderate.clip(roi),{min:1, max: 7},'drought_map',false)


// vci classification for each date


var time_start = '2001', time_end = '2024'

var ndvi2 = ee.ImageCollection("MODIS/061/MOD13A2")
.select(['NDVI'])
.filterDate(time_start, time_end);

var ndvi_min2 = ndvi2.min().multiply(0.0001);
var ndvi_max2 = ndvi2.max().multiply(0.0001);

var vci2 = ndvi2.map(function(img){
  var band = img.multiply(0.0001);
  var index = band.expression('((ndvi - min)/(max - min))*100.0',{
    'ndvi': band, 'min': ndvi_min2, 'max': ndvi_max2
    }).rename('vci');
  return index
  .copyProperties(img, ['system:time_start','system:time_end'])
  });
  
var vci_class = vci2.map(function(img){
  var cons = ee.Image.constant(0);
  var extreme = cons.where(vci_median.gte(0).and(vci_median.lt(10)), 1);
  var severe = extreme.where(vci_median.gte(10).and(vci_median.lt(20)), 2);
  var moderate = severe.where(vci_median.gte(20).and(vci_median.lt(30)), 3);
  var light = moderate.where(vci_median.gte(30).and(vci_median.lt(40)), 4);
  var no1 = light.where(vci_median.gte(40).and(vci_median.lt(60)), 5);
  var no2 = no1.where(vci_median.gte(60).and(vci_median.lt(80)), 6);
  var no3 = no2.where(vci_median.gte(80), 7);
  return no3
  .copyProperties(img, img.propertyNames())
  });
  
var vci_map = vci_class.mode();

Map.addLayer(vci_map.clip(roi),{palette: ['black','brown','red','orange','yellow', 'lightgreen','darkgreen'],
        min: 1, max: 7},'vci_mode', false)

Export.image.toDrive({
  image: vci_map.clip(roi),
  description: 'vci_map',
  region: roi,
  maxPixels: 1e13,
  crs: 'EPSG:4326',
  folder: 'drought',
  scale: 1000
  })


// drought area calculation

var drought_area = (ee.Image.pixelArea().divide(1e6)).addBands(vci_map);

print(
  ui.Chart.image.byClass(drought_area, 'constant', 
  roi, ee.Reducer.sum(), 1000, ['nan','extreme drought','severe drought','moderate drought','light drought','no drought1','nodrought2','no drought3'])
  )
