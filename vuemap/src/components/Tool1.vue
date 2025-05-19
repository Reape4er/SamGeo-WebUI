<template>
  <div class="tool-container">
    <div class="controls">
      <label for="box-threshold">Box Threshold:</label>
      <input type="range" id="box-threshold" v-model="boxThreshold" min="0" max="1" step="0.01" />
      <span>{{ boxThreshold }}</span>

      <label for="text-threshold">Text Threshold:</label>
      <input type="range" id="text-threshold" v-model="textThreshold" min="0" max="1" step="0.01" />
      <span>{{ textThreshold }}</span>

      <label for="text-prompt">Text Prompt:</label>
      <input
        type="text"
        id="text-prompt"
        v-model="textPrompt"
        placeholder="Enter your prompt here"
      />

      <label for="batch-prediction">
        <input type="checkbox" id="batch-prediction" v-model="isBatchPrediction" />
        Batch Prediction
      </label>

      <div v-if="isBatchPrediction" class="batch-params">
        <label for="tile-width">Tile Width:</label>
        <input type="number" id="tile-width" v-model="tileWidth" min="1" />

        <label for="tile-height">Tile Height:</label>
        <input type="number" id="tile-height" v-model="tileHeight" min="1" />

        <label for="overlap">Overlap (pixels):</label>
        <input type="number" id="overlap" v-model="overlap" min="0" />
      </div>

      <button @click="submit">Submit</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import axios from 'axios'

const boxThreshold = ref(0.21)
const textThreshold = ref(0.21)
const textPrompt = ref('')
const isBatchPrediction = ref(false)
const tileWidth = ref(512)
const tileHeight = ref(512)
const overlap = ref(64)
const mapStore = useMapStore()

const submit = async () => {
  const data = {
    boxThreshold: boxThreshold.value,
    textThreshold: textThreshold.value,
    textPrompt: textPrompt.value,
    batchPrediction: isBatchPrediction.value,
    // tileWidth: tileWidth.value,
    // tileHeight: tileHeight.value,
    tileSize: [tileWidth.value, tileHeight.value],
    overlap: overlap.value,
    geojson: mapStore.activeDrawnData,
  }

  try {
    const response = await axios.post('http://127.0.0.1:5000/segmentation', data)
    mapStore.setServerResponse(response.data.features)
    console.log(response.data.features)
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

label {
  font-weight: bold;
}

input[type='range'],
input[type='text'],
input[type='number'] {
  width: 100%;
  padding: 5px;
  border: 1px solid #ccc;
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

.batch-params {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}
</style>
