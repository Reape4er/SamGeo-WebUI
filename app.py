# pip install flask segment-geospatial
import shutil
from flask import Flask, abort, render_template, request, jsonify
from samgeo import tms_to_geotiff, raster_to_vector, split_raster
from samgeo.text_sam import LangSAM
import json
import os
from shapely.geometry import shape
from torch.cuda import is_available, empty_cache

os.environ['PROJ_LIB'] = r'C:\Users\UserPC\Desktop\GEOAI\venv\Lib\site-packages\rasterio\proj_data'
os.environ['GDAL_DATA'] =r'C:\Users\UserPC\Desktop\GEOAI\venv\Lib\site-packages\osgeo\data'

app = Flask(__name__)
sam = LangSAM(model_type="sam2-hiera-large")

@app.route("/")
@app.route("/map")
def show_map():
    return render_template('index.html')

@app.route("/segmentation", methods=['POST'])
def segmentation():
    data = request.get_json()
    if not data:
        abort(400, description="Request body is missing or not valid JSON")

    required_keys = ['boxThreshold', 'textThreshold', 'textPrompt', 'drawnData', 'batchPrediction']
    for key in required_keys:
        if key not in data:
            abort(400, description=f"Key '{key}' is required in the request body")

    box_threshold = float(data['boxThreshold'])
    text_threshold = float(data['textThreshold'])
    text_prompt = data['textPrompt']
    drawn_data = data['drawnData']
    batchPrediction = bool(data['batchPrediction'])
    if batchPrediction:
        tileSize = tuple(data.get('tileSize'))  
        overlap = data.get('overlap') 

    # Извлекаем bounding box
    polygon = shape(drawn_data['geometry'])
    bbox = list(polygon.bounds)
    # Загружаем карту с выделенной области
    tms_to_geotiff(
        bbox=bbox,
        output="flask_image.tif",
        source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        zoom=19,
        overwrite=True,
    )
    try:
        if batchPrediction:
            split_raster("flask_image.tif", out_dir="batch_prediction/tiles", tile_size=tileSize, overlap=overlap)


        if batchPrediction:
            sam.predict_batch(
                images="batch_prediction/tiles",
                out_dir="batch_prediction/masks",
                text_prompt=text_prompt,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
                mask_multiplier=255,
                dtype="uint8",
                merge=True,
                verbose=True,
            )
        else:
            sam.predict(
                "flask_image.tif",
                text_prompt,
                box_threshold=box_threshold, 
                text_threshold=text_threshold, 
                output="flask_mask.tif",
                # return_results=True
            )
        #очистка кэша cuda
        if is_available():
            empty_cache()

        if batchPrediction:
            raster_to_vector("batch_prediction/masks/merged.tif", "flask_mask.geojson",dst_crs="EPSG:4326")
        else:
            raster_to_vector("flask_mask.tif", "flask_mask.geojson",dst_crs="EPSG:4326")
    finally:
        # Очистка временных папок
        if os.path.exists("batch_prediction/tiles"):
            shutil.rmtree("batch_prediction/tiles")
        if os.path.exists("batch_prediction/masks"):
            shutil.rmtree("batch_prediction/masks")

    with open('flask_mask.geojson', 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    return jsonify(geojson_data)

if __name__ == '__main__':
    app.run(debug=True)