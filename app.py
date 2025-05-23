import json
import os
from shapely.geometry import shape
from flask_cors import CORS
from flask import abort, Flask, jsonify, request
from googletrans import Translator
from samgeo import raster_to_vector, split_raster, tms_to_geotiff, SamGeo2, regularize, SamGeo
from samgeo.text_sam import LangSAM
from torch.cuda import empty_cache, is_available
import shutil
import numpy as np
from werkzeug.utils import secure_filename
import tempfile
import uuid
import traceback
os.environ['PROJ_LIB'] = r'.\venv\Lib\site-packages\rasterio\proj_data'
os.environ['GDAL_DATA'] = r'.\venv\Lib\site-packages\osgeo\data'

app = Flask(__name__)
CORS(app)
print("запуск модели")
sam = LangSAM(model_type="sam2-hiera-large")
sam_point = SamGeo2(
        model_id="sam2-hiera-large",
        automatic=False,
    )

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
    if is_available():
        empty_cache()

    raster_to_vector("flask_mask.tif", "flask_mask.geojson", dst_crs="EPSG:4326")

    with open('flask_mask.geojson', 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)
    return geojson_data


# Настройки
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'tif', 'tiff', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/segmentation", methods=['POST'])
async def segmentation():
    try:
        # Проверяем наличие обязательных полей в форме
        required_fields = ['boxThreshold', 'textThreshold', 'textPrompt', 'batchPrediction']
        for field in required_fields:
            if field not in request.form:
                abort(400, description=f"Field '{field}' is required in the form data")

        # Парсим параметры
        box_threshold = float(request.form['boxThreshold'])
        text_threshold = float(request.form['textThreshold'])
        text_prompt = request.form['textPrompt']
        batch_prediction = request.form['batchPrediction'].lower() == 'true'
        
        # Обрабатываем GeoJSON или файл
        input_file_path = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                abort(400, description="No selected file")
                
            if not allowed_file(file.filename):
                abort(400, description="Invalid file type")
                
            filename = secure_filename(file.filename)
            input_file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_file_path)
            print(f"Using uploaded file: {input_file_path}")
            
        elif 'geojson' in request.form:
            try:
                drawn_data = json.loads(request.form['geojson'])
                polygon = shape(drawn_data['geometry'])
                bbox = list(polygon.bounds)
                
                print("Downloading map image...")
                input_file_path = os.path.join(UPLOAD_FOLDER, "flask_image.tif")
                tms_to_geotiff(
                    bbox=bbox,
                    output=input_file_path,
                    source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    zoom=19,
                    overwrite=True,
                )
                print(f"Map image saved to: {input_file_path}")
            except Exception as e:
                abort(400, description=f"Invalid GeoJSON data: {str(e)}")
        else:
            abort(400, description="Either file or geojson must be provided")

        # Переводим текст (если нужно)
        text_prompt = await translate_text(text_prompt)
        print(f"Translated text: {text_prompt}")

        # Обрабатываем изображение
        try:
            if batch_prediction:
                tile_size = tuple(map(int, json.loads(request.form.get('tileSize'))))
                overlap = int(request.form.get('overlap'))
                geojson_data = process_batch_segmentation(
                    input_file_path, 
                    tile_size, 
                    overlap, 
                    text_prompt, 
                    box_threshold, 
                    text_threshold
                )
            else:
                print(input_file_path)
                geojson_data = process_single_segmentation(
                    input_file_path, 
                    text_prompt, 
                    box_threshold, 
                    text_threshold
                )
        except Exception as e:
            print(f"Processing error: {str(e)}")
            abort(500, description="Image processing failed")
        finally:
            # Очистка временных файлов
            if input_file_path and os.path.exists(input_file_path):
                os.remove(input_file_path)
            if os.path.exists("batch_prediction/tiles"):
                shutil.rmtree("batch_prediction/tiles")
            if os.path.exists("batch_prediction/masks"):
                shutil.rmtree("batch_prediction/masks")

        return jsonify(geojson_data)

    except Exception as e:
        if is_available():
            empty_cache()
        print(f"Unexpected error: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/segmentation/marker', methods=['POST'])
async def segmentationByMarker():
    try:
        if request.content_type == 'application/json':
            data = request.get_json()
            file_provided = False
        else:
            data = request.form.get('data')
            if data:
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    abort(400, description="Invalid JSON in form data")
            
            file_provided = 'file' in request.files
            if file_provided:
                file = request.files['file']
                if file.filename == '':
                    abort(400, description="No selected file")
                
                # Сохраняем временный файл
                filename = secure_filename(file.filename)  # Обезопасим имя файла
                name, ext = os.path.splitext(filename)  # Разделяем имя и расширение
                random_filename = f"{name}_{uuid.uuid4().hex}{ext}"  # Добавляем UUID
                input_file_path = os.path.join(UPLOAD_FOLDER, random_filename)
                file.save(input_file_path)
                print(f"Using uploaded file: {input_file_path}")

        if not data:
            abort(400, description="Request data is missing")

        # Извлекаем координаты и метки
        coords = []
        labels = []
        for group in ("inclusion", "exclusion"):
            for feat in data.get(group, []):
                lon, lat = feat["geometry"]["coordinates"]
                coords.append((lon, lat))
                labels.append(1 if group == 'inclusion' else 0)

        print("Coordinates:", coords)
        print("Labels:", labels)

        # Обработка изображения
        if file_provided:
            # Используем загруженный файл
            image_path = input_file_path
        else:
            # Вычисляем bbox и загружаем карту
            arr = np.array(coords)
            min_lon, min_lat = arr.min(axis=0)
            max_lon, max_lat = arr.max(axis=0)

            pad = 0.3  # 20%
            dlon = (max_lon - min_lon) * pad
            dlat = (max_lat - min_lat) * pad
            bbox_padded = [
                min_lon - dlon,
                min_lat - dlat,
                max_lon + dlon,
                max_lat + dlat,
            ]

            image_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.tif")
            tms_to_geotiff(
                bbox=bbox_padded,
                output=image_path,
                source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                zoom=19,
                overwrite=True,
            )
            print("Map image downloaded to:", image_path)

        # Обработка SAM
        output_mask_path = os.path.join(UPLOAD_FOLDER, "flask_mask.tif")
        output_geojson_path = os.path.join(UPLOAD_FOLDER, "flask_mask.geojson")

        sam_point.set_image(image_path)
        sam_point.predict_by_points(
            point_coords_batch=coords,
            point_labels_batch=labels,
            point_crs="EPSG:4326",
            output=output_mask_path,
            dtype="uint8",
        )

        if is_available():
            empty_cache()

        raster_to_vector(output_mask_path, output_geojson_path, dst_crs="EPSG:4326")

        with open(output_geojson_path, 'r', encoding='utf-8') as file:
            geojson_data = json.load(file)

        # Очистка временных файлов
        for path in [image_path, output_mask_path, output_geojson_path]:
            if os.path.exists(path):
                os.remove(path)
        if file_provided and os.path.exists(input_file_path):
            os.remove(input_file_path)

        return jsonify(geojson_data)

    except Exception as e:
        if is_available():
            empty_cache()
        traceback.print_exc()
        abort(500, description=f"Internal server error: {str(e)}")

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
