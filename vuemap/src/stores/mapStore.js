import { defineStore } from 'pinia'
export const useMapStore = defineStore('map', {
  state: () => ({
    // Текущий активный режим: 'prompt', 'markers', 'multi'
    activeMode: '',
    markerMode: 'inclusion',
    drawnData: {
      promptRect: null,
      markers: {
        inclusion: [],
        exclusion: [],
      },
      multiRects: [],
    },

    serverFeatures: null,
  }),
  getters: {
    activeDrawnData() {
      switch (this.activeMode) {
        case 'prompt':
          return this.drawnData.promptRect

        case 'markers':
          return this.drawnData.markers

        case 'multi':
          return this.drawnData.multiRects
      }
    },
  },

  actions: {
    setActiveMode(mode) {
      this.activeMode = mode
    },
    setMarkerMode(mode) {
      this.markerMode = mode
    },

    saveDrawnFeature(geoJSON, type) {
      switch (this.activeMode) {
        case 'prompt':
          this.drawnData.promptRect = geoJSON
          break
        case 'markers':
          this.drawnData.markers[type].push(geoJSON)
          break
        case 'multi':
          this.drawnData.multiRects.push(geoJSON)
          console.log(this.drawnData)
          break
      }
    },

    setServerResponse(features) {
      this.serverFeatures = features
    },
    removeMarkersByGeoJSON(geoJSONCollection) {
      // Проходим по всем маркерам в inclusion и exclusion
      for (const markerType of ['inclusion', 'exclusion']) {
        this.drawnData.markers[markerType] = this.drawnData.markers[markerType].filter((marker) => {
          // Проверяем, есть ли текущий маркер в переданной коллекции для удаления
          return !geoJSONCollection.features.some(
            (featureToRemove) =>
              JSON.stringify(featureToRemove.geometry.coordinates) ===
              JSON.stringify(marker.geometry.coordinates),
          )
        })
      }
    },
    removeRectByGeoJSON(geoJSONCollection) {
      this.drawnData.multiRects = this.drawnData.multiRects.filter((rect) => {
        return !geoJSONCollection.features.some(
          (feature) =>
            JSON.stringify(feature.geometry.coordinates) ===
            JSON.stringify(rect.geometry.coordinates),
        )
      })
    },
  },
})
