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
}

export interface NavLink {
  label: string
  page: Page
  path: string
}
