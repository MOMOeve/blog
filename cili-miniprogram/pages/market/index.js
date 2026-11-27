const { locationLabel, trendText } = require('../../utils/util')
const { locations } = require('../../data/mock')

Page({
  data: {
    locationLabel: '',
    previewImage: '',
    gradeResult: null,
    quotes: [],
    updatedAt: '--'
  },

  onShow() {
    this.syncLocation()
    this.loadQuotes()
  },

  syncLocation() {
    const app = getApp()
    const loc = app.globalData.location
    const label = loc.district
      ? `${loc.city} · ${loc.district}`
      : locationLabel(loc)
    this.setData({ locationLabel: label })
  },

  onPickLocation() {
    const names = locations.map((l) => l.label)
    wx.showActionSheet({
      itemList: names,
      success: (r) => {
        const loc = locations[r.tapIndex]
        getApp().setLocation(loc)
        this.syncLocation()
        this.loadQuotes()
      }
    })
  },

  async loadQuotes() {
    const app = getApp()
    const res = await app.mockApi.fetchMarketQuotes({
      crop: 'cili',
      city: app.globalData.location.city
    })
    if (!res.ok) return
    const quotes = res.data.items.map((item) => ({
      ...item,
      trendText: trendText(item.trend, item.change)
    }))
    this.setData({ quotes, updatedAt: res.data.updatedAt })
  },

  onUploadGrade() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (r) => {
        const path = r.tempFiles[0].tempFilePath
        this.runGrade(path)
      },
      fail: () => {
        this.runGrade('mock://demo-cili.jpg')
      }
    })
  },

  async runGrade(path) {
    this.setData({
      previewImage: path.indexOf('mock://') === 0 ? '' : path
    })
    wx.showLoading({ title: '分级中…' })
    const app = getApp()
    const res = await app.mockApi.gradeCili({
      imageTempPath: path,
      location: app.globalData.location,
      unit: 'jin'
    })
    wx.hideLoading()
    if (res.ok) {
      this.setData({ gradeResult: res.data })
      wx.showToast({ title: '识别完成', icon: 'success' })
    }
  },

  goVerify() {
    wx.navigateTo({ url: '/pages/verify/index' })
  },

  goListing() {
    const g = this.data.gradeResult
    if (!g) return
    wx.navigateTo({
      url: `/pages/listing/index?grade=${encodeURIComponent(g.grade)}&price=${g.suggestPrice}&unit=${g.unit}`
    })
  }
})
