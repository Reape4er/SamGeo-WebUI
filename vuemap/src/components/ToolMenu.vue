<template>
  <div class="tool-menu">
    <div class="tool-buttons">
      <button @click="setMode('prompt')" :class="{ active: activeTool === 'prompt' }">
        По тексту
      </button>
      <button @click="setMode('markers')" :class="{ active: activeTool === 'markers' }">
        По маркерам
      </button>
      <button @click="setMode('multi')" :class="{ active: activeTool === 'multi' }">
        По выделению
      </button>
    </div>

    <div class="divider"></div>

    <div class="file-controls">
      <button class="upload-button" @click="$emit('load-photo')" :class="{ 'has-file': file }">
        {{ file ? 'Файл загружен' : 'Загрузить фото' }}
        <span v-if="file" class="file-name">{{ file.name }}</span>
      </button>
      <button v-if="file" class="clear-button" @click="$emit('clear-photo')" title="Удалить файл">
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
      </button>
    </div>

    <div class="tool-content">
      <Prompt_tool v-if="activeTool === 'prompt'" :file="file" />
      <Marker_tool v-else-if="activeTool === 'markers'" :file="file" />
      <Box_tool v-else-if="activeTool === 'multi'" :file="file" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Prompt_tool from './Prompt_tool.vue'
import Marker_tool from './Marker_tool.vue'
import Box_tool from './Box_tool.vue'
import { useMapStore } from '@/stores/mapStore'

defineEmits(['load-photo', 'clear-photo'])
const props = defineProps({
  file: {
    type: File,
  },
})
const mapStore = useMapStore()
const setMode = (mode) => {
  mapStore.setActiveMode(mode)
  activeTool.value = mode
  console.log(`Выбран инструмент: ${mode}`)
}

const activeTool = ref(null)
</script>

<style scoped>
.tool-menu {
  position: absolute;
  top: 175px;
  left: 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
  overflow: hidden;
  z-index: 10000;
}

.tool-buttons {
  display: flex;
}

button {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition:
    background 0.3s ease,
    color 0.3s ease;
}

button.active {
  background: #007bff;
  color: white;
}

button.active:hover {
  background: #0069d9;
}

button:hover:not(.active) {
  background: #f0f0f0;
}

.divider {
  height: 1px;
  background: #ddd;
}

.tool-content {
  padding: 15px;
}

.file-controls {
  display: flex;
  align-items: center;
  padding: 10px 15px;
}

.upload-button {
  flex: 1;
  padding: 10px 15px;
  border-radius: 5px;
  background-color: #f0f0f0;
  color: #333;
  text-align: left;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.upload-button.has-file {
  background-color: #e8f4ff;
  border-left: 3px solid #007bff;
}

.upload-button:hover {
  background-color: #e0e0e0;
}

.upload-button.has-file:hover {
  background-color: #d0e8ff;
}

.file-name {
  font-size: 12px;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.clear-button {
  flex: 0 0 auto; /* Не растягивается и не сжимается */
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: color 0.2s ease;
}

.clear-button:hover {
  color: #f44336;
}

.clear-button svg {
  width: 12px;
  height: 12px;
}
</style>
