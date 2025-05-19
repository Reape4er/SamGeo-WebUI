export function applyLeafletDrawPatch() {
  if (!window.L || !L.GeometryUtil) {
    console.warn('Leaflet not loaded yet, patch will be applied later');
    return false;
  }

  // Сохраняем оригинальную функцию 
  const original = L.GeometryUtil.readableArea;
  

  L.GeometryUtil.readableArea = function(area, isMetric, precision) {
    const options = L.Util.extend({}, this._options, precision);
    const type = typeof isMetric; // Фикс: объявляем переменную
    
    if (isMetric) {
      const units = type === 'string' ? [isMetric] : 
                   type === 'boolean' ? ['ha', 'm'] : isMetric;
      
      return area >= 1e6 && units.includes('km')
        ? L.GeometryUtil.formattedNumber(area / 1e6, options.km) + ' km²'
        : area >= 1e4 && units.includes('ha')
          ? L.GeometryUtil.formattedNumber(area / 1e4, options.ha) + ' ha'
          : L.GeometryUtil.formattedNumber(area, options.m) + ' m²';
    }
    
    area /= 0.836127;
    return area >= 3097600
      ? L.GeometryUtil.formattedNumber(area / 3097600, options.mi) + ' mi²'
      : area >= 4840
        ? L.GeometryUtil.formattedNumber(area / 4840, options.ac) + ' acres'
        : L.GeometryUtil.formattedNumber(area, options.yd) + ' yd²';
  };

  console.log('Leaflet Draw patch successfully applied');
  return true;
}

if (import.meta.hot) {
  import.meta.hot.accept(() => {
    applyLeafletDrawPatch();
  });
}