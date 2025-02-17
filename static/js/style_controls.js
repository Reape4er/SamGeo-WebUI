document.addEventListener('DOMContentLoaded', function() {
    const layerSelect = document.getElementById('layer-select');
    const colorInput = document.getElementById('color');
    const weightInput = document.getElementById('weight');
    const opacityInput = document.getElementById('opacity');

    // Функция для обновления стиля слоя
    function updateLayerStyle() {
        const selectedLayerKey = layerSelect.value;
        const selectedLayer = window.layers[selectedLayerKey];

        if (selectedLayer) {
            const newStyle = {
                color: colorInput.value,
                weight: parseInt(weightInput.value),
                fillOpacity: parseFloat(opacityInput.value),
            };

            // Применяем стиль к слою
            selectedLayer.setStyle(newStyle);

            // Обновляем внутренний объект стилей
            selectedLayer.options.style = newStyle;
        }
    }

    // Обработчики изменений параметров стиля
    colorInput.addEventListener('input', updateLayerStyle);
    weightInput.addEventListener('input', updateLayerStyle);
    opacityInput.addEventListener('input', updateLayerStyle);

    // Обработчик изменения выбранного слоя
    layerSelect.addEventListener('change', function() {
        const selectedLayerKey = this.value;
        const selectedLayer = window.layers[selectedLayerKey];

        if (selectedLayer) {
            const { color, weight, fillOpacity } = selectedLayer.options.style;

            // Устанавливаем значения в поля ввода
            colorInput.value = color;
            weightInput.value = weight;
            opacityInput.value = fillOpacity;
        }
    });
});