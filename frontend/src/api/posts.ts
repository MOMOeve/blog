import { apiFetch } from './client'
import type { Comment, Post, PostDetail } from '../types'

export interface PaginatedResult<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export const POSTS_PAGE_SIZE = 12

export interface FetchPostsParams {
  category?: string
  tag?: string
  year?: number
  month?: number
  search?: string
  featured?: boolean
  published?: boolean
  ordering?: string
  page?: number
}

export async function fetchPostsPage(params: FetchPostsParams = {}): Promise<PaginatedResult<Post>> {
  const query = new URLSearchParams()
  if (params.category && params.category !== '全部') query.set('category', params.category)
  if (params.tag) query.set('tag', params.tag)
  if (params.year) query.set('year', String(params.year))
  if (params.month) query.set('month', String(params.month))
  if (params.search) query.set('search', params.search)
  if (params.featured) query.set('featured', 'true')
  if (params.published === false) query.set('published', 'false')
  if (params.published === true) query.set('published', 'true')
  if (params.ordering) query.set('ordering', params.ordering)
  if (params.page && params.page > 1) query.set('page', String(params.page))

  const qs = query.toString()
  const path = qs ? `/posts/?${qs}` : '/posts/'
  const data = await apiFetch<PaginatedResult<Post> | Post[]>(path)
  if (Array.isArray(data)) {
    return { count: data.length, next: null, previous: null, results: data }
  }
  return data
}

export async function fetchPosts(params: FetchPostsParams = {}): Promise<Post[]> {
  const data = await fetchPostsPage(params)
  return data.results
}

export async function fetchDrafts(): Promise<Post[]> {
  return fetchPosts({ published: false, ordering: '-updated_at' })
}

export async function fetchPost(id: number): Promise<PostDetail> {
  return apiFetch(`/posts/${id}/`)
}

export async function togglePostLike(id: number): Promise<{ likeCount: number; liked: boolean }> {
  return apiFetch(`/posts/${id}/like/`, { method: 'POST' })
}

export async function fetchPostComments(postId: number): Promise<Comment[]> {
  return apiFetch(`/posts/${postId}/comments/`)
}

export async function createComment(postId: number, body: string): Promise<Comment & { detail?: string }> {
  return apiFetch(`/posts/${postId}/comments/`, {
    method: 'POST',
    body: JSON.stringify({ body }),
  })
}

export async function fetchCategoryNames(): Promise<string[]> {
  return apiFetch<string[]>('/posts/categories-list/')
}

export interface TagCloudItem {
  name: string
  count: number
}

export interface ArchiveItem {
  year: number
  month: number
  count: number
}

export async function fetchTagCloud(): Promise<TagCloudItem[]> {
  return apiFetch<TagCloudItem[]>('/posts/tag-cloud/')
}

export async function fetchArchive(): Promise<ArchiveItem[]> {
  return apiFetch<ArchiveItem[]>('/posts/archive/')
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
