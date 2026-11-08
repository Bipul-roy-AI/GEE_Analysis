// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'forest';
var BD_SOURCE = '00051_landsat_wildfire';
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

var cor1 = [-121.30739155546495,37.83353662375529]

var geometry = BD_ROI

var table = BD_COUNTRY

var roi = BD_COUNTRY

Map.centerObject(roi)
Map.addLayer(roi)

var viirs = ee.ImageCollection("NASA/VIIRS/002/VNP09GA")
.select(['I1','I2'])
.filterDate('2017-10-08','2017-10-10')

Map.addLayer(viirs.toBands().clip(roi),[],'viirs_wildfire', false)


var cor2 = [
  [-123.45801418605573,38.81836572068789],
  [-122.44589870754011,38.81836572068789],
  [-122.44589870754011,39.64593638831554],
  [-123.45801418605573,39.64593638831554],
  [-123.45801418605573,38.81836572068789]
  ]

var geometry2 = BD_ROI

Map.centerObject(geometry2)

var before = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
.select(['SR_.*'])
.filterDate('2016','2017')
.filter(ee.Filter.calendarRange(8, 10, 'month'))
.filterBounds(geometry2);

Map.addLayer(before.median().clip(geometry2),{bands: ['SR_B5','SR_B4','SR_B3']},'before_rgb',false)

var after = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
.select(['SR_.*'])
.filterDate('2018','2019')
.filter(ee.Filter.calendarRange(8, 10, 'month'))
.filterBounds(geometry2);

Map.addLayer(after.median().clip(geometry2),{bands: ['SR_B5','SR_B4','SR_B3']},'after_rgb',false)


print(before.first())

var ndvi_before = before.map(function(img){
  var gain = ee.Number(img.get('REFLECTANCE_MULT_BAND_5'))
  var offset = ee.Number(img.get('REFLECTANCE_ADD_BAND_3'))
  var sr = img.multiply(gain).add(offset)
  var ndvi = sr.normalizedDifference(['SR_B5','SR_B4']).rename('ndvi_before');
  return ndvi
  }).median();
  

var ndvi_after = after.map(function(img){
  var gain = ee.Number(img.get('REFLECTANCE_MULT_BAND_5'))
  var offset = ee.Number(img.get('REFLECTANCE_ADD_BAND_3'))
  var sr = img.multiply(gain).add(offset)
  var ndvi = sr.normalizedDifference(['SR_B5','SR_B4']).rename('ndvi_before');
  return ndvi
  }).median();


Map.addLayer(ndvi_before.clip(geometry2),[],'ndvi_before', false)
Map.addLayer(ndvi_after.clip(geometry2),[],'ndvi_after', false)

// print(
//   ui.Chart.image.histogram(ndvi_before, geometry2, 100)
//   .setOptions({
//     title: 'NDVI before (2016)'
//     })
//   )

// print(
//   ui.Chart.image.histogram(ndvi_after, geometry2, 100)
//   .setOptions({
//     title: 'NDVI after (2018)'
//     })
//   )


var ndvi_change = ndvi_before.subtract(ndvi_after);

Map.addLayer(ndvi_change.clip(geometry2), [], 'ndvi_change', false)

var water_mask = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
.select('label').mode().eq(0).not();

Map.addLayer(water_mask.clip(geometry2), [], 'water_mask', false)

var ndvi_change_masked = ndvi_change.updateMask(water_mask).rename('ndvi_change');

Map.addLayer(ndvi_change_masked.clip(geometry2), [], 'ndvi_change_masked', false)

Export.image.toDrive({
  image: ndvi_change_masked.clip(geometry2),
  description: 'wildfire_change', 
  scale: 100, 
  maxPixels: 1e13, 
  region: geometry2, 
  crs: 'EPSG:4326'
  })

// print(
//   ui.Chart.image.histogram(ndvi_change_masked, geometry2, 100)
//   )


var thr = ndvi_change_masked.gt(0.1);
var mask = thr.updateMask(thr);

Map.addLayer(mask.clip(geometry2),[],'mask',false)

var area = mask.multiply(ee.Image.pixelArea().divide(1e6));

var final_area = ee.Number(area.reduceRegion(ee.Reducer.sum(), geometry2, 1000).values().get(0))

print(final_area)


