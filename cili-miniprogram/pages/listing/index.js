const { locationLabel } = require('../../utils/util')

Page({
  data: {
    grade: '一级',
    price: '8.5',
    unit: '斤',
    quantity: '100',
    locationLabel: '',
    loading: false
  },

  onLoad(query) {
    const app = getApp()
    this.setData({
      grade: query.grade ? decodeURIComponent(query.grade) : '一级',
      price: query.price || '8.5',
      unit: query.unit || '斤',
      locationLabel: locationLabel(app.globalData.location)
    })
  },

  onGrade(e) {
    this.setData({ grade: e.detail.value })
  },
  onPrice(e) {
    this.setData({ price: e.detail.value })
  },
  onQty(e) {
    this.setData({ quantity: e.detail.value })
  },

  async onSubmit() {
    this.setData({ loading: true })
    const app = getApp()
    const res = await app.mockApi.createListing({
      grade: this.data.grade,
      price: Number(this.data.price),
      unit: this.data.unit,
      quantity: Number(this.data.quantity),
      location: app.globalData.location
    })
    this.setData({ loading: false })
    if (!res.ok) {
      wx.showToast({ title: res.error.message, icon: 'none' })
      return
    }
    wx.showModal({
      title: '挂售成功（Mock）',
      content: `挂售单号 ${res.data.listingId}`,
      showCancel: false,
      success: () => wx.navigateBack()
    })
  }
})
