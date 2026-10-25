function upsertMeta(attribute: 'name' | 'property', key: string, content: string) {
  let element = document.head.querySelector(`meta[${attribute}="${key}"]`) as HTMLMetaElement | null
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, key)
    document.head.appendChild(element)
  }
  element.content = content
}

export function updatePageSeo(options: {
  title: string
  description: string
  url?: string
  image?: string
  type?: string
}) {
  document.title = options.title
  upsertMeta('name', 'description', options.description)
  upsertMeta('property', 'og:title', options.title)
  upsertMeta('property', 'og:description', options.description)
  upsertMeta('property', 'og:type', options.type || 'website')
  if (options.image) upsertMeta('property', 'og:image', options.image)

  let canonical = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
  if (!canonical) {
    canonical = document.createElement('link')
    canonical.rel = 'canonical'
    document.head.appendChild(canonical)
  }
  canonical.href = options.url || window.location.href
}
