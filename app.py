# pip install flask segment-geospatial
from flask import Flask, render_template, request, jsonify
from samgeo import tms_to_geotiff, raster_to_vector
from samgeo.text_sam import LangSAM
import json
import os
from shapely.geometry import shape
from torch.cuda import is_available, empty_cache
os.environ['PROJ_LIB'] = r'C:\Users\UserPC\Desktop\GEOAI\venv\Lib\site-packages\rasterio\proj_data'
os.environ['GDAL_DATA'] =r'C:\Users\UserPC\Desktop\GEOAI\venv\Lib\site-packages\osgeo\data'

app = Flask(__name__)

@app.route("/")
@app.route("/map")
def show_map():
    return render_template('index.html')

@app.route("/segmentation", methods=['POST'])
def segmentation():
    data = request.get_json()
    box_threshold = float(data.get('boxThreshold'))
    text_threshold = float(data.get('textThreshold'))
    text_prompt = data.get('textPrompt')
    drawn_data = data.get('drawnData')
    
    # извлекаем bounding box
    polygon = shape(drawn_data['geometry'])
    bbox = list(polygon.bounds)

    tms_to_geotiff(
        bbox=bbox,
        output="flask_image.tif",
        source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        zoom=19,
        overwrite=True,
    )

    sam = LangSAM(model_type="sam2-hiera-large")
    ans = sam.predict(
        "flask_image.tif",
        text_prompt,
        box_threshold=box_threshold, 
        text_threshold=text_threshold, 
        output="flask_mask.tif",
        return_results=True
    )
    #очистка кэша cuda
    if is_available():
        empty_cache()

    print(ans)
    raster_to_vector("flask_mask.tif", "flask_mask.geojson",dst_crs="EPSG:4326")
    with open('flask_mask.geojson', 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    return jsonify(geojson_data)
if __name__ == '__main__':
    app.run(debug=True)