// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'agriculture';
var BD_SOURCE = '0128_gee_cropland_rainfed_irrigated';
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



// Tutorial Code by Amirhossein Ahrari
// YouTube: https://www.youtube.com/@amirhosseinahrarigee
// Tutorial Video: Google Earth Engine Tutorial-133: Irrigated and Rainfed Cropland Mapping

// This code is part of a tutorial series on Earth Engine programming techniques
// presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
// this code for academic and non-academic purposes. Don't forget to subscribe to
// the Amirhossein Ahrari channel and follow the videos to support the instructor

var table = BD_COUNTRY


var cor1 = [46.06447471590808,37.4664136308292] 

var geometry = BD_ROI


var cropland = ee.ImageCollection("projects/sat-io/open-datasets/GFSAD/LGRIP30").mosaic()

Map.addLayer(cropland,{min: 0, max: 3}, 'cropland', false)

Map.addLayer(table, [], 'basins',false)

var roi = BD_ROI

Map.addLayer(roi, [],'roi_basin', false)

Map.centerObject(roi)

Map.addLayer(cropland.clip(roi), {min: 0, max: 3}, 'roi_cropland', false)

Export.image.toDrive({
  image: cropland.clip(roi), 
  description: 'cropland_roi', 
  scale: 100, 
  region: roi, 
  crs: 'EPSG:4326', 
  maxPixels: 1e13, 
  folder: 'test'
  })
  
  

var cor2 = [
  [45.65420086591323,36.5852635591113],
  [46.599025084663225,36.5852635591113], 
  [46.599025084663225,37.24404911390012], 
  [45.65420086591323,37.24404911390012], 
  [45.65420086591323,36.5852635591113]
  ]

var geometry2 = BD_ROI

var irrigated = cropland.eq(2).selfMask()

Map.addLayer(irrigated.clip(roi),[],'irrigated',false)


var irrigated_vec = irrigated.reduceToVectors({
  geometry: geometry2, scale: 100
  })
  
Map.addLayer(irrigated_vec,[],'irrigated_vec',false)


Export.table.toDrive({
  collection: irrigated_vec, description: 'irrigated_vector', fileFormat: 'SHP'
  })


var ndvi = ee.ImageCollection("MODIS/061/MOD13Q1")
.filterDate('2020','2025')
.map(function(img){
  return img.select('NDVI').multiply(0.0001)
  .copyProperties(img, img.propertyNames())
  })


print(
  ui.Chart.image.series(ndvi, irrigated_vec, ee.Reducer.mean(),
  250, 'system:time_start')
  )

var cor3 = [
  [46.20901043622573,36.542743443804014], 
  [46.48366863935073,36.542743443804014], 
  [46.48366863935073,36.76749276467415], 
  [46.20901043622573,36.76749276467415], 
  [46.20901043622573,36.542743443804014]
  ]

var geometry3 = BD_ROI

var rainfed = cropland.eq(3).selfMask()

var rainfed_vec = rainfed.reduceToVectors({
  geometry: geometry3, scale: 100
  })
  
Map.addLayer(rainfed_vec,[],'rainfed_vec',false)


print(
  ui.Chart.image.series(ndvi, rainfed_vec, ee.Reducer.mean(),
  250, 'system:time_start')
  )

