import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NavButton from '../components/NavButton.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // 注册自定义全局组件
    app.component('NavButton', NavButton)
  }
} satisfies Theme