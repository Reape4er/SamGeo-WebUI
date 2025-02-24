import json
import os
from shapely.geometry import shape

from flask import abort, Flask, jsonify, render_template, request
from googletrans import Translator
from samgeo import raster_to_vector, split_raster, tms_to_geotiff
from samgeo.text_sam import LangSAM
from torch.cuda import empty_cache, is_available

import shutil

os.environ['PROJ_LIB'] = r'C:\Users\UserPC\Desktop\GEOAI\venv\Lib\site-packages\rasterio\proj_data'
os.environ['GDAL_DATA'] = r'C:\Users\UserPC\Desktop\GEOAI\venv\Lib\site-packages\osgeo\data'

app = Flask(__name__)
print("запуск модели")
sam = LangSAM(model_type="sam2-hiera-large")
translator = Translator()

async def translate_text(text, src='ru', dest='en'):
    async with Translator() as translator:
        result = await translator.translate(text, dest, src)
        print(result)
        return result.text

def process_batch_segmentation(image_path, tileSize, overlap, text_prompt, box_threshold, text_threshold):
    print("сплит")
    split_raster(image_path, out_dir="batch_prediction/tiles", tile_size=tileSize, overlap=overlap)

    print("предсказание батчей")
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

    print("очистка кэша")
    if is_available():
        empty_cache()

    raster_to_vector("batch_prediction/masks/merged.tif", "flask_mask.geojson", dst_crs="EPSG:4326")

    with open('flask_mask.geojson', 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    return geojson_data

def process_single_segmentation(image_path, text_prompt, box_threshold, text_threshold):
    print("предсказание")
    sam.predict(
        image_path,
        text_prompt,
        box_threshold=box_threshold, 
        text_threshold=text_threshold, 
        output="flask_mask.tif",
    )

    print("очистка кэша")
    print(is_available())
    if is_available():
        empty_cache()

    raster_to_vector("flask_mask.tif", "flask_mask.geojson", dst_crs="EPSG:4326")

    with open('flask_mask.geojson', 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    return geojson_data

@app.route("/")
@app.route("/map")
def show_map():
    return render_template('index.html')

@app.route("/segmentation", methods=['POST'])
async def segmentation():
    print("Принято")
    data = request.get_json()
    if not data:
        abort(400, description="Request body is missing or not valid JSON")

    required_keys = ['boxThreshold', 'textThreshold', 'textPrompt', 'drawnData', 'batchPrediction']
    for key in required_keys:
        if key not in data:
            abort(400, description=f"Key '{key}' is required in the request body")

    print("Извлечение")
    box_threshold = float(data['boxThreshold'])
    text_threshold = float(data['textThreshold'])
    text_prompt = data['textPrompt']
    drawn_data = data['drawnData']
    batchPrediction = bool(data['batchPrediction'])

    print("перевод текста")
    text_prompt = await translate_text(text_prompt)
    print(f"Переведенный текст: {text_prompt}")

    polygon = shape(drawn_data['geometry'])
    bbox = list(polygon.bounds)
    print("загрузка карты")

    tms_to_geotiff(
        bbox=bbox,
        output="flask_image.tif",
        source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        zoom=19,
        overwrite=True,
    )

    try:
        if batchPrediction:
            tileSize = tuple(data.get('tileSize'))  
            overlap = data.get('overlap') 
            geojson_data = process_batch_segmentation("flask_image.tif", tileSize, overlap, text_prompt, box_threshold, text_threshold)
        else:
            geojson_data = process_single_segmentation("flask_image.tif", text_prompt, box_threshold, text_threshold)
    except Exception as e:
        print(e)
        return abort(500, "server error")
    finally:
        if os.path.exists("batch_prediction/tiles"):
            shutil.rmtree("batch_prediction/tiles")
        if os.path.exists("batch_prediction/masks"):
            shutil.rmtree("batch_prediction/masks")

    return jsonify(geojson_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, use_reloader=False, debug=True)
