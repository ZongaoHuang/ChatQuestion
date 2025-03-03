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


          { text: '第一模块A', link: '/first_A' },
          { text: '第二模块A', link: '/second_A' },
          { text: '第二模块A', link: '/second_A1' },

          { text: 'indexb', link: '/indexB' },
          { text: '第一模块B', link: '/first_B' },
          { text: '第二模块B', link: '/second_B' },
          { text: '第二模块B1', link: '/second_B1' },

          { text: '第三模块', link: '/third' },
          { text: '报告下载', link: '/report' },
        ]
      }
    ],
  },
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:17771',  // 后端地址
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/')
        },
        '/media': {
          target: 'http://127.0.0.1:17771',
          changeOrigin: true
        }
      }
    }
  }
})
