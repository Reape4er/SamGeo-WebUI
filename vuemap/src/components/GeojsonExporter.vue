<template>
  <div class="geojson-exporter">
    <div class="layers-list">
      <div v-for="(layer, index) in layersWithNames" :key="index" class="layer-item">
        <input type="checkbox" v-model="selectedLayers[index]" :id="'layer-' + index" />
        <label :for="'layer-' + index">
          {{ layer.name || `Слой ${index + 1}` }}
          <span class="feature-count">({{ layer.featureCount }} объектов)</span>
        </label>
      </div>
    </div>

    <button @click="downloadSelectedLayers" :disabled="!hasSelectedLayers" class="download-button">
      Скачать выбранные слои
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import JSZip from 'jszip'

const props = defineProps({
  featuresLayers: {
    type: Array,
    required: true,
    default: () => [],
  },
})

const selectedLayers = ref([])

watch(
  () => props.featuresLayers,
  (newLayers) => {
    selectedLayers.value = new Array(newLayers.length).fill(true)
  },
  { immediate: true },
)

const layersWithNames = computed(() => {
  return props.featuresLayers.map((layer, index) => {
    const geoJSON = layer.toGeoJSON()
    const featureCount = geoJSON.type === 'FeatureCollection' ? geoJSON.features.length : 1

    return {
      name: layer.options.name || `Слой ${index + 1}`,
      featureCount,
      geoJSON,
    }
  })
})

const hasSelectedLayers = computed(() => {
  return selectedLayers.value.some((selected) => selected)
})

const downloadSelectedLayers = async () => {
  const zip = new JSZip()

  layersWithNames.value.forEach((layer, index) => {
    if (selectedLayers.value[index]) {
      const fileName = `${layer.name.replace(/[^a-z0-9]/gi, '_')}.geojson`
      const geoJSONStr = JSON.stringify(layer.geoJSON, null, 2)
      zip.file(fileName, geoJSONStr)
    }
  })

  const content = await zip.generateAsync({ type: 'blob' })
  const url = URL.createObjectURL(content)
  const link = document.createElement('a')
  link.href = url
  link.download = 'geojson_layers.zip'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.geojson-exporter {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  max-width: 300px;
  z-index: 1000;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.layers-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 1rem;
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.layers-list::-webkit-scrollbar {
  width: 6px;
}

.layers-list::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

.layer-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
}

.layer-item:last-child {
  border-bottom: none;
}

.layer-item label {
  margin-left: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #333;
}

.feature-count {
  color: #666;
  font-size: 0.8rem;
  margin-left: 0.5rem;
  opacity: 0.8;
}

.download-button {
  width: 100%;
  padding: 0.6rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.download-button:hover {
  background-color: #3d8b40;
  transform: translateY(-1px);
}

.download-button:disabled {
  background-color: #a5a5a5;
  cursor: not-allowed;
  transform: none;
}
</style>
