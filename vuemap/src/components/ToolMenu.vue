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

    <div class="tool-content">
      <Prompt_tool v-if="activeTool === 'prompt'" />
      <Marker_tool v-else-if="activeTool === 'markers'" />
      <div v-else-if="activeTool === 'multi'">Инструмент 3 (заглушка)</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Prompt_tool from './Prompt_tool.vue'
import Marker_tool from './Marker_tool.vue'
import { useMapStore } from '@/stores/mapStore'

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

/* Новый стиль для наведения на активную кнопку */
button.active:hover {
  background: #0069d9; /* Темнее синий */
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
</style>
