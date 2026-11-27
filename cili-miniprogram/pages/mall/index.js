const { products } = require('../../data/mock')

const categories = [
  { id: 'all', name: '全部', icon: '◎' },
  { id: 'pesticide', name: '农药', icon: '盾' },
  { id: 'fertilizer', name: '肥料', icon: '肥' },
  { id: 'sapling', name: '树苗', icon: '苗' },
  { id: 'product', name: '刺梨产品', icon: '果' }
]

Page({
  data: {
    categories: categories.slice(1),
    products,
    filtered: products,
    activeCat: 'all',
    keyword: ''
  },

  onShow() {
    this.applyFilter()
  },

  onSearch(e) {
    this.setData({ keyword: e.detail.value }, () => this.applyFilter())
  },

  onCat(e) {
    const id = e.currentTarget.dataset.id
    const next = this.data.activeCat === id ? 'all' : id
    this.setData({ activeCat: next }, () => this.applyFilter())
  },

  applyFilter() {
    const { products: list, activeCat, keyword } = this.data
    const kw = (keyword || '').trim()
    const filtered = list.filter((p) => {
      const catOk = activeCat === 'all' || p.category === activeCat
      const kwOk =
        !kw ||
        p.name.indexOf(kw) >= 0 ||
        p.categoryLabel.indexOf(kw) >= 0 ||
        p.spec.indexOf(kw) >= 0
      return catOk && kwOk
    })
    this.setData({ filtered })
  },

  goDetail(e) {
    wx.navigateTo({
      url: `/pages/product-detail/index?id=${e.currentTarget.dataset.id}`
    })
  },

  addCart(e) {
    wx.showToast({ title: '已加入购物车（Mock）', icon: 'success' })
  }
})
