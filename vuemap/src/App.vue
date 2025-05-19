<template>
  <myComponents />
</template>

<script setup>
import { onMounted } from 'vue'
import myComponents from './components/myComponents.vue'
import { applyLeafletDrawPatch } from './utils/leaflet-draw-patch'

// Применяем патч при монтировании приложения
onMounted(() => {
  // Пытаемся применить сразу
  if (!applyLeafletDrawPatch()) {
    // Если Leaflet еще не загружен, пробуем каждые 100мс
    const interval = setInterval(() => {
      if (applyLeafletDrawPatch()) {
        clearInterval(interval)
      }
    }, 100)
  }
})
</script>

<style>
body,
html {
  margin: 0;
  padding: 0;
  overflow: hidden;
  font-family: 'Roboto', sans-serif;
}
</style>
