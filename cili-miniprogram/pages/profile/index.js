Page({
  data: {
    role: 'farmer',
    unread: 0
  },

  onShow() {
    const app = getApp()
    this.setData({
      role: app.globalData.role,
      unread: app.globalData.unreadMessages
    })
  },

  onSwitchRole(e) {
    const role = e.currentTarget.dataset.role
    getApp().setRole(role)
    this.setData({ role })
    wx.showToast({
      title: role === 'farmer' ? '已切换为农民' : '已切换为买家',
      icon: 'none'
    })
  },

  goOrders(e) {
    const status = e.currentTarget.dataset.status || ''
    wx.navigateTo({
      url: `/pages/orders/index?status=${status}`
    })
  },

  goMessages() {
    wx.navigateTo({ url: '/pages/messages/index' })
  },

  onAddress() {
    wx.showToast({ title: '地址管理（Mock）', icon: 'none' })
  },

  onSettings() {
    wx.showToast({ title: '设置（Mock）', icon: 'none' })
  }
})
