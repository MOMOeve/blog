Page({
  data: { plan: null },

  async onLoad(query) {
    wx.showLoading({ title: '加载中' })
    const res = await getApp().mockApi.fetchPlantingPlan(query.id)
    wx.hideLoading()
    if (res.ok) this.setData({ plan: res.data })
  }
})
