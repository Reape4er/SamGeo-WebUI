from flask import Flask, render_template, request, send_file
from samgeo import tms_to_geotiff
from samgeo.text_sam import LangSAM

import os
os.environ['PROJ_LIB'] = r'C:\Users\UserPC\GEOAI\GEOAI-venv\Lib\site-packages\rasterio\proj_data'
os.environ['GDAL_DATA'] =r'C:\Users\UserPC\GEOAI\GEOAI-venv\Lib\site-packages\osgeo\data'

app = Flask(__name__)

# Извлечение bounding box
def extract_bbox_from_drawn_data(drawn_data):
    if drawn_data and len(drawn_data) > 0:
        geometry = drawn_data[0]['geometry']
        coordinates = geometry['coordinates'][0]
        min_xy = coordinates[0]
        max_xy = coordinates[2]

        return [min_xy,max_xy]
    return None

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

    bbox = extract_bbox_from_drawn_data(drawn_data)
    print(bbox)

    tms_to_geotiff(
        bbox=[bbox[0][0],bbox[0][1],bbox[1][0],bbox[1][1]],
        output="flask_image.tif",
        source='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        zoom=19,
        overwrite=True,
    )
    # использую модель "sam2-hiera-tiny" из-за того что слабо нагружает пк, лучше использовать "sam2-hiera-large"
    # sam = LangSAM(model_type="sam2-hiera-tiny")
    sam = LangSAM(model_type="sam2-hiera-large")
    sam.predict("flask_image.tif", text_prompt, box_threshold=box_threshold, text_threshold=text_threshold, output="flask_mask.tif")

    return send_file("flask_mask.tif", mimetype='image/tiff')

if __name__ == '__main__':
    app.run(debug=True)