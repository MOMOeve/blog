/** 页面展示用静态模拟数据 */

const products = [
  {
    id: 'p1',
    name: '有机肥',
    category: 'fertilizer',
    categoryLabel: '肥料',
    spec: '25kg / 袋',
    price: 68,
    originPrice: 88,
    badge: '性价比',
    usage: '每亩建议施用 80–100kg，花前深施。',
    compare: [
      { shop: '黔南农资', price: 72 },
      { shop: '惠水供销', price: 68 },
      { shop: '线上仓', price: 65 }
    ],
    desc: '腐熟有机肥，适合刺梨园基肥与追肥。'
  },
  {
    id: 'p2',
    name: '刺梨苗',
    category: 'sapling',
    categoryLabel: '树苗',
    spec: '一年生实生苗',
    price: 2.98,
    originPrice: 4.5,
    badge: '热销',
    usage: '株距 1.5m × 行距 2m，栽后浇透定根水。',
    compare: [
      { shop: '长顺苗圃', price: 3.2 },
      { shop: '惠水苗场', price: 2.98 },
      { shop: '六盘水种苗', price: 3.5 }
    ],
    desc: '贵州本地适种刺梨苗，成活率高。'
  },
  {
    id: 'p3',
    name: '专用农药',
    category: 'pesticide',
    categoryLabel: '农药',
    spec: '500ml',
    price: 36.8,
    originPrice: 45,
    badge: '性价比',
    usage: '稀释 800–1000 倍喷雾，花期慎用。',
    compare: [
      { shop: '植保站', price: 38 },
      { shop: '惠水农资', price: 36.8 },
      { shop: '县域仓', price: 39 }
    ],
    desc: '针对刺梨常见病虫害的专用复配制剂。'
  },
  {
    id: 'p4',
    name: '刺梨果干',
    category: 'product',
    categoryLabel: '刺梨产品',
    spec: '200g / 盒',
    price: 29.9,
    originPrice: 39.9,
    badge: '新品',
    usage: '开袋即食，密封避光保存。',
    compare: [
      { shop: '本店', price: 29.9 },
      { shop: '特产馆', price: 32 },
      { shop: '商超', price: 35 }
    ],
    desc: '原果低温烘干，保留维生素 C。'
  },
  {
    id: 'p5',
    name: '刺梨原汁',
    category: 'product',
    categoryLabel: '刺梨产品',
    spec: '1L / 瓶',
    price: 48,
    originPrice: 58,
    badge: '推荐',
    usage: '冷藏后饮用口感更佳。',
    compare: [
      { shop: '本店', price: 48 },
      { shop: '特产馆', price: 52 }
    ],
    desc: '鲜榨刺梨原汁，无额外蔗糖。'
  },
  {
    id: 'p6',
    name: '复合肥',
    category: 'fertilizer',
    categoryLabel: '肥料',
    spec: '50kg / 袋',
    price: 128,
    originPrice: 148,
    badge: '性价比',
    usage: '果期追肥每株 0.3–0.5kg。',
    compare: [
      { shop: '供销社', price: 132 },
      { shop: '惠水农资', price: 128 }
    ],
    desc: '氮磷钾均衡配方，适配刺梨果期需求。'
  }
]

const marketQuotes = [
  {
    id: 'm1',
    name: '惠水县农贸市场',
    low: 8.0,
    high: 9.0,
    unit: '斤',
    change: 0.3,
    trend: 'up'
  },
  {
    id: 'm2',
    name: '长顺县交易市场',
    low: 7.8,
    high: 8.8,
    unit: '斤',
    change: 0.2,
    trend: 'up'
  },
  {
    id: 'm3',
    name: '贵阳市花溪市场',
    low: 8.2,
    high: 9.2,
    unit: '斤',
    change: 0,
    trend: 'flat'
  },
  {
    id: 'm4',
    name: '罗甸县水果批发市场',
    low: 7.5,
    high: 8.5,
    unit: '斤',
    change: -0.1,
    trend: 'down'
  }
]

const orders = [
  {
    id: 'o1001',
    status: 'pending_pay',
    statusLabel: '待付款',
    productName: '有机肥 25kg',
    quantity: 2,
    amount: 136,
    createdAt: '2026-11-26 14:20'
  },
  {
    id: 'o1002',
    status: 'pending_ship',
    statusLabel: '待发货',
    productName: '刺梨苗 × 50',
    quantity: 50,
    amount: 149,
    createdAt: '2026-11-25 09:12'
  },
  {
    id: 'o1003',
    status: 'pending_recv',
    statusLabel: '待收货',
    productName: '专用农药 500ml',
    quantity: 3,
    amount: 110.4,
    createdAt: '2026-11-24 16:48'
  },
  {
    id: 'o1004',
    status: 'done',
    statusLabel: '已完成',
    productName: '刺梨果干 200g',
    quantity: 5,
    amount: 149.5,
    createdAt: '2026-11-20 11:05'
  }
]

const messages = [
  {
    id: 'msg1',
    from: '惠水农资客服',
    preview: '您的有机肥订单已备货，预计明日发货。',
    time: '10:22',
    unread: true
  },
  {
    id: 'msg2',
    from: '长顺苗圃',
    preview: '刺梨苗库存充足，可安排物流上门。',
    time: '昨天',
    unread: true
  },
  {
    id: 'msg3',
    from: '刺梨收购助手',
    preview: '今日农事建议已更新，点击查看详情。',
    time: '周一',
    unread: false
  }
]

const locations = [
  { province: '贵州', city: '六盘水', district: '', label: '贵州 · 六盘水', lat: 26.59, lng: 104.83 },
  { province: '贵州', city: '黔南州', district: '惠水县', label: '黔南州 · 惠水县', lat: 26.14, lng: 106.66 },
  { province: '贵州', city: '黔南州', district: '长顺县', label: '黔南州 · 长顺县', lat: 26.02, lng: 106.45 },
  { province: '贵州', city: '贵阳', district: '花溪区', label: '贵阳 · 花溪', lat: 26.41, lng: 106.67 }
]

module.exports = {
  products,
  marketQuotes,
  orders,
  messages,
  locations
}
