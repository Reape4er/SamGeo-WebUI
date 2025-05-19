<template>
  <div class="layer-control">
    <div class="control-group">
      <label for="layer-select">Слой:</label>
      <select id="layer-select" v-model="selectedLayerIndex" @change="setSelectedColor">
        <option v-for="(layer, index) in layers" :key="index" :value="index">
          GeoJSON Layer {{ index + 1 }}
        </option>
      </select>
    </div>

    <div class="control-group" v-if="selectedLayerIndex !== null">
      <label for="color-select">Цвет:</label>
      <input type="color" id="color-select" v-model="selectedColor" @input="updateLayerStyle" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  layers: {
    type: Array,
    required: true,
    validator: (value) => value.every((layer) => typeof layer.setStyle === 'function'),
  },
})

const selectedLayerIndex = ref(null)
const selectedColor = ref('#0000ff')

function updateLayerStyle() {
  if (selectedLayerIndex.value === null || !props.layers[selectedLayerIndex.value]) return

  const style = {
    color: selectedColor.value,
    weight: 2,
    opacity: 1,
    fillColor: selectedColor.value,
    fillOpacity: 0.3,
  }

  props.layers[selectedLayerIndex.value].setStyle(style)
}

function setSelectedColor() {
  const layer = props.layers[selectedLayerIndex.value]
  if (!layer) return

  // 1. Проверяем напрямую установленные стили
  if (layer.options.color) {
    selectedColor.value = layer.options.color
    return
  }

  // 2. Для GeoJSON слоёв проверяем внутренний рендерер
  if (layer._layers) {
    const firstFeature = Object.values(layer._layers)[0]
    if (firstFeature?.options?.color) {
      selectedColor.value = firstFeature.options.color
      return
    }
  }

  selectedColor.value = '#0000ff'
}
</script>

<style scoped>
.layer-control {
  position: fixed;
  top: 10px;
  right: 160px;
  background: rgba(255, 255, 255, 0.85);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-width: 250px;
}

.control-group {
  margin-bottom: 10px;
}

.control-group:last-child {
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

select,
input[type='color'] {
  width: 100%;
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

input[type='color'] {
  height: 35px;
  padding: 2px;
}
</style>
