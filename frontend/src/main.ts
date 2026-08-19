import { createApp } from 'vue'
import './styles/global.less'
import App from './App.vue'
import { initRouter } from './router'

initRouter()
createApp(App).mount('#app')
