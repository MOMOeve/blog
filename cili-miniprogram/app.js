const { mockApi } = require('./utils/mock-api')

App({
  globalData: {
    role: 'farmer', // farmer | buyer
    location: {
      province: '贵州',
      city: '六盘水',
      district: '',
      lat: 26.59,
      lng: 104.83
    },
    unreadMessages: 2
  },

  mockApi,

  onLaunch() {
    try {
      const role = wx.getStorageSync('cili_role')
      if (role) this.globalData.role = role
      const loc = wx.getStorageSync('cili_location')
      if (loc) this.globalData.location = loc
    } catch (e) {
      // ignore storage errors in tourist mode
    }
  },

  setRole(role) {
    this.globalData.role = role
    try {
      wx.setStorageSync('cili_role', role)
    } catch (e) {}
  },

  setLocation(location) {
    this.globalData.location = location
    try {
      wx.setStorageSync('cili_location', location)
    } catch (e) {}
  }
})
