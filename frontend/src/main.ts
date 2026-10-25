import { createApp } from 'vue'
import './styles/global.less'

if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => undefined))
}
import App from './App.vue'
import { initRouter } from './router'

initRouter()
createApp(App).mount('#app')
