<template>
  <div class="marker-tool">
    <div class="marker-mode-buttons">
      <button
        @click="changeMarkerMode('inclusion')"
        :class="{ active: mapStore.markerMode === 'inclusion' }"
      >
        Выбор объектов
      </button>
      <button
        @click="changeMarkerMode('exclusion')"
        :class="{ active: mapStore.markerMode === 'exclusion' }"
      >
        Обозначение фона
      </button>
    </div>
    <button class="segment-button" @click="submit">Сегментировать</button>
  </div>
</template>

<script setup>
import { useMapStore } from '@/stores/mapStore'
import axios from 'axios'
const props = defineProps({
  file: {
    type: File,
  },
})
const mapStore = useMapStore()

const changeMarkerMode = (mode) => {
  mapStore.setMarkerMode(mode)
}

const submit = async () => {
  console.log(props.file)
  const formData = new FormData()

  if (props.file) {
    formData.append('file', props.file)
  }
  formData.append(
    'data',
    JSON.stringify({
      inclusion: mapStore.activeDrawnData.inclusion || [],
      exclusion: mapStore.activeDrawnData.exclusion || [],
    }),
  )

  try {
    const response = await axios.post('http://127.0.0.1:5000/segmentation/marker', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    mapStore.setServerResponse(response.data.features)
    console.log(response.data)
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
.marker-tool {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.marker-mode-buttons {
  display: flex;
  gap: 8px;
  width: 100%;
}

.marker-mode-buttons button {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #f8f9fa;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.marker-mode-buttons button:hover {
  background-color: #e9ecef;
  border-color: #ced4da;
}

.marker-mode-buttons button.active {
  background-color: #007bff;
  border-color: #007bff;
  color: white;
}

.segment-button {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #007bff;
  border-radius: 6px;
  background: #007bff;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease;
}

.segment-button:hover {
  background-color: #0069d9;
  border-color: #0062cc;
}
</style>
