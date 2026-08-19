import { apiFetch } from './client'

export interface UploadResult {
  url: string
  path: string
  name: string
  size: number
}

/** Staff 上传图片：multipart field `file` → `{ url, path, ... }` */
export async function uploadImage(file: File): Promise<UploadResult> {
  const form = new FormData()
  form.append('file', file)
  return apiFetch<UploadResult>('/uploads/', {
    method: 'POST',
    body: form,
  })
}
