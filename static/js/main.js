var map = L.map('map').setView([55.751244, 37.618423], 10); // Создаем и центрируем карту на Москве

L.tileLayer(
    'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Esri',
    name: 'Esri Satellite'
}).addTo(map);

function removeLeafletAttribution() {
    const leafletLink = document.querySelector('#map > div.leaflet-control-container > div.leaflet-bottom.leaflet-right > div > a');
    const separator = document.querySelector('#map > div.leaflet-control-container > div.leaflet-bottom.leaflet-right > div > span');

    if (leafletLink) {
        leafletLink.remove();
    }
    if (separator) {
        separator.remove();
    }
}
removeLeafletAttribution();

// Инициализируем объект overlays и добавляем контроллер слоев
var overlays = {};
var layerControl = null;

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    draw: {
        polyline: false,
        polygon: false,
        circle: false,
        circlemarker: false,
        marker: false,
        rectangle: true
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

// Сохранение последней созданной области
var drawnData = null;
map.on('draw:created', function (event) {
    drawnItems.clearLayers();
    var layer = event.layer;
    drawnItems.addLayer(layer);
    drawnData = layer.toGeoJSON(); 
    console.log(drawnData)
});

document.getElementById('box-threshold').addEventListener('input', function() {
    document.getElementById('box-threshold-value').textContent = this.value;
});

document.getElementById('text-threshold').addEventListener('input', function() {
    document.getElementById('text-threshold-value').textContent = this.value;
});

// Обработка чекбокса для отображения параметров батчевого предсказания
document.getElementById('batch-prediction').addEventListener('change', function() {
    var batchParams = document.getElementById('batch-params');
    batchParams.style.display = this.checked ? 'block' : 'none';
});

// Инициализация объекта для хранения слоев
window.layers = {};

// Функция для добавления нового слоя
function addLayerToControl(name, layer) {
    window.layers[name] = layer; 
    layerControl.addOverlay(layer, name);
    updateLayerSelect();
}

// Функция для обновления выпадающего списка слоев
function updateLayerSelect() {
    var layerSelect = document.getElementById('layer-select');
    layerSelect.innerHTML = ''; // Очищаем список

    for (var name in window.layers) {
        var option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        layerSelect.appendChild(option);
    }
}

async function sendData() {
    try {
        // Получение и подготовка значений из элементов управления 
        const batchPrediction = document.getElementById('batch-prediction').checked;

        const data = {
            boxThreshold: document.getElementById('box-threshold').value,
            textThreshold: document.getElementById('text-threshold').value,
            textPrompt: document.getElementById('text-prompt').value,
            drawnData: drawnData,
            batchPrediction: batchPrediction,
            tileSize: batchPrediction ? [parseInt(document.getElementById('tile-width').value), parseInt(document.getElementById('tile-height').value)] : null,
            overlap: batchPrediction ? parseInt(document.getElementById('overlap').value) : null
        };

        // Отправка данных на локальный сервер
        const response = await fetch('http://192.168.0.101:9000/segmentation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        const geojson = await response.json();
        if (!response.ok) {
            throw new Error('Ошибка сети: ' + response.statusText);
        }
        console.log(geojson.features);

        // Создаем новый GeoJSON слой
        var geojsonLayer = L.geoJSON(geojson, {
            style: {
                color: "#ff0000",
                weight: 2,
                fillOpacity: 0.3
            }
        }).addTo(map);

        // Добавляем слой в контроллер и обновляем интерфейс
        var layerName = "GeoJSON Layer " + Object.keys(overlays).length;
        overlays[layerName] = geojsonLayer;


        if (!layerControl) {
            layerControl = L.control.layers(null, overlays).addTo(map);
        } else {

            layerControl.addOverlay(geojsonLayer, layerName);
            
        }
        window.layers[layerName] = geojsonLayer; 
        updateLayerSelect();

        addGeoJSONToList(layerName, geojson);

    } catch (error) {
        console.error('Ошибка:', error);
    }
}
// Добавляем новый geojson в список для загруки
function addGeoJSONToList(layerName, geojson) {
    const listItem = document.createElement('li');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = layerName;
    checkbox.name = layerName;
    checkbox.value = JSON.stringify(geojson); 

    const label = document.createElement('label');
    label.htmlFor = layerName;
    label.textContent = layerName;

    listItem.appendChild(checkbox);
    listItem.appendChild(label);

    document.getElementById('geojson-list').appendChild(listItem);
}
function downloadSelectedLayers() {
    const selectedLayers = [];
    const checkboxes = document.querySelectorAll('#geojson-list input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        selectedLayers.push({
            name: checkbox.id, 
            data: JSON.parse(checkbox.value) 
        });
    });

    if (selectedLayers.length === 0) {
        alert('Выберите хотя бы один слой для скачивания.');
        return;
    }

    // Создаем ZIP-архив
    const zip = new JSZip();

    // Добавляем каждый выбранный слой в архив
    selectedLayers.forEach((layer) => {
        const fileName = `${layer.name}.geojson`;
        const fileContent = JSON.stringify(layer.data, null, 2);
        zip.file(fileName, fileContent); 
    });

    // Генерируем архив и скачиваем его
    zip.generateAsync({ type: "blob" })
        .then(function (content) {
            saveAs(content, "geojson_layers.zip");
        })
        .catch(function (error) {
            console.error("Ошибка при создании архива:", error);
        });
}
