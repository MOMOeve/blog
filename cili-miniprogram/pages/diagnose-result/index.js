Page({
  data: {
    result: {
      name: '',
      severity: 'medium',
      confidence: 0,
      summary: '',
      symptoms: [],
      treatments: [],
      productIds: []
    },
    image: '',
    severityLabel: '',
    confidence: ''
  },

  onLoad(query) {
    let result = null
    try {
      if (query.payload) result = JSON.parse(decodeURIComponent(query.payload))
    } catch (e) {}
    if (!result) {
      result = {
        name: '刺梨白粉病（疑似）',
        severity: 'medium',
        confidence: 0.78,
        summary: '演示数据：叶片出现白色粉状物。',
        symptoms: ['叶面白色粉斑'],
        treatments: [{ title: '农业防治', detail: '清除病叶，改善通风。' }],
        productIds: ['p3']
      }
    }
    const map = { low: '低', medium: '中', high: '高' }
    this.setData({
      result,
      image: query.image ? decodeURIComponent(query.image) : '',
      severityLabel: map[result.severity] || result.severity,
      confidence: Math.round((result.confidence || 0) * 100) + '%'
    })
  },

  goMall() {
    wx.switchTab({ url: '/pages/mall/index' })
  }
})
