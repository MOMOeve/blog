import { apiFetch } from './client'
import type { Photo } from '../types'

export async function fetchPhotos(params: { category?: string } = {}): Promise<Photo[]> {
  const query = new URLSearchParams()
  if (params.category && params.category !== '全部') {
    query.set('category', params.category)
  }
  const qs = query.toString()
  const path = qs ? `/photos/?${qs}` : '/photos/'
  return apiFetch<Photo[]>(path)
}

export async function fetchPhotoCategories(): Promise<string[]> {
  return apiFetch<string[]>('/photos/categories-list/')
}
