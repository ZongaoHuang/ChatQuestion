import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config


export default defineConfig({
  title: "产品营销推广研究",
  description: "产品营销推广研究",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      
    ],

    sidebar: [
      {
        text: '模块',
        items: [
          { text: '第一模块', link: '/first' },
          { text: '第二模块A', link: '/second_A' },
          { text: '第二模块A', link: '/second_A1' },
          { text: '第三模块', link: '/third' }
        ]
      }
    ],


  }
})
