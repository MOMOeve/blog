function formatPrice(n) {
  const num = Number(n)
  if (Number.isNaN(num)) return '--'
  return num % 1 === 0 ? String(num) : num.toFixed(2)
}

function trendText(trend, change) {
  if (trend === 'up') return `涨 ${Math.abs(change)}`
  if (trend === 'down') return `跌 ${Math.abs(change)}`
  return '持平'
}

function locationLabel(loc) {
  if (!loc) return '选择位置'
  if (loc.district) return `${loc.city} · ${loc.district}`
  return `${loc.province} · ${loc.city}`
}

module.exports = {
  formatPrice,
  trendText,
  locationLabel
}
