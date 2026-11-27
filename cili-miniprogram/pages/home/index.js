const { locationLabel } = require('../../utils/util')
const { locations } = require('../../data/mock')

Page({
  data: {
    locationLabel: '',
    advice: null
  },

  onShow() {
    this.syncLocation()
    this.loadAdvice()
  },

  syncLocation() {
    const app = getApp()
    this.setData({ locationLabel: locationLabel(app.globalData.location) })
  },

  async loadAdvice() {
    const app = getApp()
    const res = await app.mockApi.fetchTodayAdvice({
      location: app.globalData.location,
      crop: 'cili'
    })
    if (res.ok) this.setData({ advice: res.data })
  },

  onPickLocation() {
    const names = locations.map((l) => l.label)
    wx.showActionSheet({
      itemList: names,
      success: async (r) => {
        const loc = locations[r.tapIndex]
        const app = getApp()
        const res = await app.mockApi.resolveLocation({
          manual: {
            province: loc.province,
            city: loc.city,
            district: loc.district
          }
        })
        if (res.ok) {
          app.setLocation({
            province: res.data.province,
            city: res.data.city,
            district: res.data.district,
            lat: loc.lat,
            lng: loc.lng
          })
          this.syncLocation()
          this.loadAdvice()
          wx.showToast({ title: '位置已更新', icon: 'success' })
        }
      }
    })
  },

  goPlantingPlan() {
    const planId = (this.data.advice && this.data.advice.planId) || 'plan-cili-flower'
    wx.navigateTo({ url: `/pages/planting-plan/index?id=${planId}` })
  },

  onDiagnose() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: async (r) => {
        const path = r.tempFiles[0].tempFilePath
        wx.showLoading({ title: '识别中…' })
        const app = getApp()
        const res = await app.mockApi.diagnoseCrop({
          imageTempPath: path,
          crop: 'cili',
          location: app.globalData.location
        })
        wx.hideLoading()
        if (!res.ok) {
          wx.showToast({ title: res.error.message, icon: 'none' })
          return
        }
        const q = encodeURIComponent(JSON.stringify(res.data))
        wx.navigateTo({
          url: `/pages/diagnose-result/index?payload=${q}&image=${encodeURIComponent(path)}`
        })
      },
      fail: async () => {
        // 开发者工具未授权相机时，走纯 mock 演示
        wx.showLoading({ title: '演示识别…' })
        const app = getApp()
        const res = await app.mockApi.diagnoseCrop({
          imageTempPath: 'mock://demo-leaf.jpg',
          crop: 'cili',
          location: app.globalData.location
        })
        wx.hideLoading()
        if (res.ok) {
          const q = encodeURIComponent(JSON.stringify(res.data))
          wx.navigateTo({ url: `/pages/diagnose-result/index?payload=${q}` })
        }
      }
    })
  },

  async onVoiceQa() {
    wx.showLoading({ title: '语音理解中…' })
    const app = getApp()
    const res = await app.mockApi.voiceQa({
      text: '刺梨现在怎么浇水？',
      location: app.globalData.location
    })
    wx.hideLoading()
    if (!res.ok) {
      wx.showToast({ title: res.error.message, icon: 'none' })
      return
    }
    const tips = (res.data.relatedTips || []).map((t) => `· ${t}`).join('\n')
    wx.showModal({
      title: '语音问答（Mock）',
      content: `问：${res.data.transcript}\n\n答：${res.data.answer}\n\n${tips}`,
      showCancel: false,
      confirmText: '知道了'
    })
  }
})
