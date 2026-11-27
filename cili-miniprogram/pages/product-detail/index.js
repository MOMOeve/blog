const { products } = require('../../data/mock')

Page({
  data: { product: null },

  onLoad(query) {
    const product = products.find((p) => p.id === query.id) || products[0]
    this.setData({ product })
  },

  addCart() {
    wx.showToast({ title: '已加入购物车（Mock）', icon: 'success' })
  },

  async buyNow() {
    const p = this.data.product
    wx.showLoading({ title: '下单中…' })
    const app = getApp()
    const res = await app.mockApi.createOrder({
      productId: p.id,
      productName: p.name,
      quantity: 1,
      amount: p.price
    })
    wx.hideLoading()
    if (res.ok) {
      wx.showModal({
        title: '下单成功（Mock）',
        content: `订单号 ${res.data.orderId}，状态：待付款`,
        confirmText: '查看订单',
        success: (r) => {
          if (r.confirm) wx.navigateTo({ url: '/pages/orders/index' })
        }
      })
    }
  }
})
