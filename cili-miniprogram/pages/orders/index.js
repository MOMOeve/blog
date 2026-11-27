const { orders } = require('../../data/mock')

Page({
  data: {
    tabs: [
      { id: '', label: '全部' },
      { id: 'pending_pay', label: '待付款' },
      { id: 'pending_ship', label: '待发货' },
      { id: 'pending_recv', label: '待收货' },
      { id: 'done', label: '已完成' }
    ],
    active: '',
    list: orders
  },

  onLoad(query) {
    const active = query.status || ''
    this.setData({ active }, () => this.filter())
  },

  onTab(e) {
    this.setData({ active: e.currentTarget.dataset.id }, () => this.filter())
  },

  filter() {
    const { active } = this.data
    const list = active ? orders.filter((o) => o.status === active) : orders
    this.setData({ list })
  }
})
