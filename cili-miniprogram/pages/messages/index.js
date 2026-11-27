const { messages } = require('../../data/mock')

Page({
  data: { list: messages },

  onShow() {
    const unread = this.data.list.filter((m) => m.unread).length
    getApp().globalData.unreadMessages = unread
  },

  onOpen(e) {
    const id = e.currentTarget.dataset.id
    const list = this.data.list.map((m) =>
      m.id === id ? { ...m, unread: false } : m
    )
    this.setData({ list })
    getApp().globalData.unreadMessages = list.filter((m) => m.unread).length
    const msg = list.find((m) => m.id === id)
    wx.showModal({
      title: msg.from,
      content: msg.preview,
      showCancel: false
    })
  }
})
