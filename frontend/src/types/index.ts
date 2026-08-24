export type Page = '首页' | '文章' | '摄影' | '关于' | '联系'

export interface Post {
  id: number
  title: string
  titleEn: string
  category: string
  date: string
  readTime: string
  excerpt: string
  img: string
  featured?: boolean
  published?: boolean
  tags: string[]
  viewCount?: number
  likeCount?: number
}

export interface PostNavItem {
  id: number
  title: string
}

export interface PostDetail extends Post {
  body?: string
  liked?: boolean
  related?: Post[]
  prev?: PostNavItem | null
  next?: PostNavItem | null
}

export interface Comment {
  id: number
  body: string
  authorName: string
  createdAt: string
  approved?: boolean
}

export interface Photo {
  id: number
  title: string
  location: string
  date: string
  img: string
  aspect: 'landscape' | 'portrait'
  category: string
  description: string
  sort_order?: number
  published?: boolean
}

export interface NavLink {
  label: string
  page: Page
  path: string
}
