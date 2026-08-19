import { apiFetch } from './client'
import type { Post } from '../types'

interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export async function fetchPosts(params: {
  category?: string
  search?: string
  featured?: boolean
  published?: boolean
  ordering?: string
} = {}): Promise<Post[]> {
  const query = new URLSearchParams()
  if (params.category && params.category !== '全部') query.set('category', params.category)
  if (params.search) query.set('search', params.search)
  if (params.featured) query.set('featured', 'true')
  if (params.published === false) query.set('published', 'false')
  if (params.published === true) query.set('published', 'true')
  if (params.ordering) query.set('ordering', params.ordering)

  const qs = query.toString()
  const path = qs ? `/posts/?${qs}` : '/posts/'
  const data = await apiFetch<Paginated<Post> | Post[]>(path)
  return Array.isArray(data) ? data : data.results
}

export async function fetchDrafts(): Promise<Post[]> {
  return fetchPosts({ published: false, ordering: '-updated_at' })
}

export async function fetchPost(id: number): Promise<Post & { body?: string; published?: boolean }> {
  return apiFetch(`/posts/${id}/`)
}

export async function fetchCategoryNames(): Promise<string[]> {
  return apiFetch<string[]>('/posts/categories-list/')
}

export interface PostWritePayload {
  title: string
  titleEn?: string
  category: string
  tags?: string[]
  excerpt: string
  body?: string
  img?: string
  readTime?: string
  featured?: boolean
  published?: boolean
}

export async function createPost(
  payload: PostWritePayload,
): Promise<Post & { body?: string; published?: boolean }> {
  return apiFetch('/posts/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updatePost(
  id: number,
  payload: PostWritePayload,
): Promise<Post & { body?: string; published?: boolean }> {
  return apiFetch(`/posts/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function patchPost(
  id: number,
  payload: Partial<PostWritePayload>,
): Promise<Post & { body?: string; published?: boolean }> {
  return apiFetch(`/posts/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function deletePost(id: number): Promise<void> {
  return apiFetch(`/posts/${id}/`, { method: 'DELETE' })
}
