import { apiFetch } from './client'
import type { Photo } from '../types'

export interface PhotoWritePayload {
  title: string
  location?: string
  date?: string
  img: string
  aspect?: 'landscape' | 'portrait'
  category: string
  description?: string
  sort_order?: number
  published?: boolean
}

export async function fetchPhotos(params: { category?: string } = {}): Promise<Photo[]> {
  const query = new URLSearchParams()
  if (params.category && params.category !== '全部') {
    query.set('category', params.category)
  }
  const qs = query.toString()
  const path = qs ? `/photos/?${qs}` : '/photos/'
  const data = await apiFetch<Photo[] | { results: Photo[] }>(path)
  return Array.isArray(data) ? data : data.results
}

export async function fetchPhoto(id: number): Promise<Photo> {
  return apiFetch(`/photos/${id}/`)
}

export async function fetchPhotoCategories(): Promise<string[]> {
  return apiFetch<string[]>('/photos/categories-list/')
}

export async function createPhoto(payload: PhotoWritePayload): Promise<Photo> {
  return apiFetch('/photos/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updatePhoto(id: number, payload: Partial<PhotoWritePayload>): Promise<Photo> {
  return apiFetch(`/photos/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function deletePhoto(id: number): Promise<void> {
  return apiFetch(`/photos/${id}/`, { method: 'DELETE' })
}
