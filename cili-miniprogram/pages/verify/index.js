Page({
  data: {
    image: '',
    loading: false,
    result: null,
    score: ''
  },

  onPick() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (r) => {
        this.setData({ image: r.tempFiles[0].tempFilePath, result: null })
      },
      fail: () => {
        this.setData({ image: '', result: null })
        wx.showToast({ title: '将使用演示图验货', icon: 'none' })
      }
    })
  },

  async onVerify() {
    this.setData({ loading: true })
    const app = getApp()
    const res = await app.mockApi.verifyVariety({
      sampleImageTempPath: this.data.image || 'mock://sample.jpg',
      expectedVariety: '贵农5号'
    })
    this.setData({ loading: false })
    if (!res.ok) {
      wx.showToast({ title: res.error.message, icon: 'none' })
      return
    }
    this.setData({
      result: res.data,
      score: Math.round(res.data.score * 100) + '%'
    })
  }
})
