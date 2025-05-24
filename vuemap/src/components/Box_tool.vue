<template>
  <div class="tool-container">
    <div class="controls">
      <p class="info-text">В этом режиме требуется выделить несколько объектов</p>

      <button @click="submit">Сегментировать</button>
    </div>
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

const submit = async () => {
  console.log(props.file)
  const formData = new FormData()

  if (props.file) {
    formData.append('file', props.file)
  }
  formData.append('geojsons', JSON.stringify(mapStore.activeDrawnData))
  try {
    const response = await axios.post('http://127.0.0.1:5000/segmentation/boxes', formData, {
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
.tool-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 10px;
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-text {
  margin: 0;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 5px;
}

button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease;
}

button:hover {
  background: #0056b3;
}
</style>
