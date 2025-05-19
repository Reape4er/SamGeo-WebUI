<template>
  <div ref="mapContainer" class="map-container"></div>
  <LayerControl v-show="hasFeatures" :layers="featuresLayers" />
  <GeoJSONExporter v-show="hasFeatures" :featuresLayers="featuresLayers" />
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import L, { featureGroup } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw'
import 'leaflet-draw/dist/leaflet.draw.css'
import LayerControl from './LayerControl.vue'
import GeoJSONExporter from './GeojsonExporter.vue'

const props = defineProps({
  center: { type: Array, default: () => [55.751244, 37.618423] },
  zoom: { type: Number, default: 13 },
  tileLayerUrl: {
    type: String,
    default:
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  },
  tileLayerOptions: {
    type: Object,
    default: () => ({ attribution: 'Esri', name: 'Esri Satellite' }),
  },
})

const mapStore = useMapStore()
const mapContainer = ref(null)
const hasFeatures = computed(() => featuresLayers.value.length > 0)

let map = null
let drawControl = null
let layersControl = null
const previousPromptLayer = ref(null)
const markerLayer = L.featureGroup()

const featuresLayers = ref([])

const createMarkerIcon = (color) => {
  return L.divIcon({
    className: `${color}-marker`,
    html: `<div style="background: ${color}; width: 10px; height: 10px; border-radius: 50%; border: 2px solid white"></div>`,
    iconSize: [10, 10],
  })
}

const getCurrentMarkerStyle = () => {
  return {
    icon: createMarkerIcon(mapStore.markerMode === 'inclusion' ? 'green' : 'red'),
    repeatMode: true,
  }
}

const drawModes = {
  prompt: {
    rectangle: true,
    marker: false,
    polyline: false,
    polygon: false,
    circle: false,
    circlemarker: false,
  },
  markers: {
    marker: getCurrentMarkerStyle(),
    rectangle: false,
    polyline: false,
    polygon: false,
    circle: false,
    circlemarker: false,
  },
  multi: {
    rectangle: true,
    marker: false,
    polyline: false,
    polygon: false,
    circle: false,
    circlemarker: false,
  },
}

function updateDrawControl() {
  if (!map) return

  drawModes.markers.marker = getCurrentMarkerStyle()

  if (drawControl) {
    map.removeControl(drawControl)
  }

  drawControl = new L.Control.Draw({
    draw: drawModes[mapStore.activeMode],
    edit: {
      featureGroup: markerLayer,
      remove: mapStore.activeMode === 'markers' ? true : false,
      edit: false,
    },
  })

  map.addControl(drawControl)
}

function handleDrawCreated(e) {
  const layer = e.layer
  const geoJSON = layer.toGeoJSON()

  switch (mapStore.activeMode) {
    case 'prompt':
      clearPreviousPromptLayer()
      map.addLayer(layer)
      previousPromptLayer.value = layer
      mapStore.saveDrawnFeature(geoJSON, null)
      break

    case 'markers':
      if (layer instanceof L.Marker) {
        layer.setIcon(getCurrentMarkerStyle().icon)
        markerLayer.addLayer(layer)

        mapStore.saveDrawnFeature(geoJSON, mapStore.markerMode)
      }
      break

    case 'multi':
      map.addLayer(layer)
      mapStore.saveDrawnFeature(geoJSON, 'multi')
      break
  }
}

function clearPreviousPromptLayer() {
  if (previousPromptLayer.value) {
    map.removeLayer(previousPromptLayer.value)
    previousPromptLayer.value = null
  }
}

function setupMap() {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value).setView(props.center, props.zoom)
  map.attributionControl.remove()
  const baseLayer = L.tileLayer(props.tileLayerUrl, props.tileLayerOptions).addTo(map)

  markerLayer.addTo(map)
  layersControl = L.control.layers({ 'Base Layer': baseLayer }).addTo(map)

  map.on('draw:created', handleDrawCreated)
  map.on('draw:deleted', handleDrawDeleted)
}
function handleDrawDeleted(e) {
  mapStore.removeMarkersByGeoJSON(e.layers.toGeoJSON())
}
function addFeaturesLayer(features) {
  if (!features?.length || !map) return

  const layer = L.geoJSON(features, {
    style: {
      color: '#0000ff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.5,
    },
  }).addTo(map)

  featuresLayers.value.push(layer)

  if (layersControl) {
    layersControl.addOverlay(layer, `Features Layer ${featuresLayers.value.length}`)
  }
}

onMounted(() => {
  setupMap()
  updateDrawControl()
})

watch(() => mapStore.activeMode, updateDrawControl)
watch(() => mapStore.markerMode, updateDrawControl)
watch(() => mapStore.serverFeatures, addFeaturesLayer)
</script>

<style scoped>
.map-container {
  height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 0;
}
</style>
