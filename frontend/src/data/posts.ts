import type { Post } from '../types'

export const HERO_IMG =
  'https://images.unsplash.com/photo-1783152982779-b41307148345?w=1800&h=900&fit=crop&auto=format'

export const posts: Post[] = [
  {
    id: 1,
    title: '用 TypeScript 重写了整个项目之后',
    titleEn: 'After Rewriting the Entire Project in TypeScript',
    category: '代码',
    date: '2026年8月14日',
    readTime: '10 分钟',
    excerpt:
      '花了两周时间把一个积累了三年的 JavaScript 项目迁移到 TypeScript。过程痛苦，结果值得——不只是类型安全，更是一次强迫自己重新理解整个代码结构的机会。',
    img: 'https://images.unsplash.com/photo-1783152982779-b41307148345?w=900&h=500&fit=crop&auto=format',
    featured: true,
    tags: ['代码', 'TypeScript'],
  },
  {
    id: 2,
    title: 'JLPT N2 备考：那些真正有用的方法',
    titleEn: 'JLPT N2 Prep: Methods That Actually Worked',
    category: '语言',
    date: '2026年7月28日',
    readTime: '8 分钟',
    excerpt:
      '备考六个月，刷了三套真题，最后以 142 分通过。回头看，有些方法确实有效，有些完全是在浪费时间。这篇写给同样在准备 N2 的你。',
    img: 'https://images.unsplash.com/photo-1634896974114-cadd2782d5bc?w=700&h=420&fit=crop&auto=format',
    tags: ['语言', 'JLPT'],
  },
  {
    id: 3,
    title: '深夜写代码是一种什么体验',
    titleEn: 'What It Feels Like to Code at 2 AM',
    category: '生活',
    date: '2026年7月10日',
    readTime: '5 分钟',
    excerpt:
      '凌晨两点，一个 bug 终于复现了。窗外的城市安静下来，屏幕的光是房间里唯一的颜色。这种时刻有一种奇怪的专注，像是整个世界只剩下你和这段代码。',
    img: 'https://images.unsplash.com/photo-1501420264597-23296a7e6a46?w=700&h=420&fit=crop&auto=format',
    tags: ['生活', '随笔'],
  },
  {
    id: 4,
    title: 'React 状态管理：我从 Redux 换到了 Zustand',
    titleEn: 'State Management: Why I Switched from Redux to Zustand',
    category: '代码',
    date: '2026年6月22日',
    readTime: '7 分钟',
    excerpt:
      '不是说 Redux 不好，而是对于中型项目，它的样板代码确实太多了。Zustand 让我写得更少，想得更清楚。附上迁移过程中踩过的几个坑。',
    img: 'https://images.unsplash.com/photo-1512641406448-6574e777bec6?w=700&h=420&fit=crop&auto=format',
    tags: ['代码', 'React'],
  },
  {
    id: 5,
    title: '为什么我用语言给变量命名（开玩笑的）',
    titleEn: 'Why I Name Variables in Japanese (Just Kidding)',
    category: '语言',
    date: '2026年6月5日',
    readTime: '4 分钟',
    excerpt:
      '学语言和写代码有一个共同点：你以为你理解了，直到你试着用它解释一件事，才发现自己其实一知半解。语言学习就像 debug，总在意想不到的地方出错。',
    img: 'https://images.unsplash.com/photo-1415025148099-17fe74102b28?w=700&h=420&fit=crop&auto=format',
    tags: ['语言', '随笔'],
  },
  {
    id: 6,
    title: '记录一次完整的个人项目从零到上线',
    titleEn: 'A Full Journey: From Zero to Deployed Side Project',
    category: '代码',
    date: '2026年5月18日',
    readTime: '12 分钟',
    excerpt:
      '从想法到上线用了四十天。技术栈选择、数据库设计、部署踩坑，以及最后没人用的轻微沮丧——全都记在这里了。',
    img: 'https://images.unsplash.com/photo-1785680975815-59f143d1479d?w=700&h=420&fit=crop&auto=format',
    tags: ['代码', '项目'],
  },
]

export const allPosts: Post[] = [
  ...posts,
  {
    id: 7,
    title: 'Anki 用了两年之后，我的诚实评价',
    titleEn: 'My Honest Review of Anki After Two Years',
    category: '语言',
    date: '2026年5月3日',
    readTime: '6 分钟',
    excerpt:
      'Anki 不是万能的，但它确实改变了我记单词的方式。间隔重复这件事一旦理解了原理，就很难再用其他方法。聊聊我怎么建牌、怎么坚持的。',
    img: 'https://images.unsplash.com/photo-1509023464722-18d996393ca8?w=800&h=480&fit=crop&auto=format',
    tags: ['语言', '工具'],
  },
  {
    id: 8,
    title: '我的开发环境配置（2026版）',
    titleEn: 'My Dev Environment Setup (2026 Edition)',
    category: '代码',
    date: '2026年4月15日',
    readTime: '9 分钟',
    excerpt:
      'Terminal、编辑器、常用工具、字体、主题……每隔一段时间整理一次自己的开发环境，其实也是一次审视自己工作习惯的机会。',
    img: 'https://images.unsplash.com/photo-1556811246-b2d9eb3fbad0?w=800&h=480&fit=crop&auto=format',
    tags: ['代码', '工具'],
  },
  {
    id: 9,
    title: '从零开始学 N3 文法的那半年',
    titleEn: 'The Six Months I Spent Learning N3 Grammar from Zero',
    category: '语言',
    date: '2026年3月28日',
    readTime: '11 分钟',
    excerpt:
      '「〜ところだ」和「〜ばかりだ」到底有什么区别？学语言的人都懂那种感觉：每搞懂一个文法，就又发现一个更令人头大的。但这就是乐趣所在。',
    img: 'https://images.unsplash.com/photo-1504493408076-2017927bbb1a?w=800&h=480&fit=crop&auto=format',
    tags: ['语言', '文法'],
  },
]

export const categories = ['全部', '代码', '语言', '生活', '随笔']

export const navLinks = [
  { label: '首页', page: '首页' as const, path: '/' },
  { label: '文章', page: '文章' as const, path: '/articles' },
  { label: '摄影', page: '摄影' as const, path: '/photography' },
  { label: '关于', page: '关于' as const, path: '/about' },
  { label: '联系', page: '联系' as const, path: '/contact' },
]

export const sidebarTags = [
  'TypeScript',
  'React',
  '语言',
  'JLPT',
  '随笔',
  '工具',
  '项目',
  '生活',
  '踩坑',
]
