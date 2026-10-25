import { apiFetch } from './client'

export interface ContactPayload {
  name: string
  email: string
  subject?: string
  message: string
}

export interface ContactMessage {
  id: number
  name: string
  email: string
  subject: string
  message: string
  createdAt: string
}

export interface SubscribeResult {
  id: number
  email: string
  createdAt: string
  detail?: string
}

export async function submitContact(payload: ContactPayload): Promise<ContactMessage> {
  return apiFetch('/contact/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function subscribeNewsletter(email: string): Promise<SubscribeResult> {
  return apiFetch('/subscribe/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}
