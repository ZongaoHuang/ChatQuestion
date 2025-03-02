<template>
    <div 
      class="button-container" 
      :style="{ justifyContent: align === 'right' ? 'flex-end' : align, paddingRight: align === 'right' ? '1.5rem' : 0 }"
    >
      <button class="nav-button" @click="navigate">
        {{ buttonText }}
      </button>
    </div>
</template>
  
<script setup>
  import { defineProps } from 'vue'
  import { useRouter } from 'vitepress'
  
  const props = defineProps({
    buttonText: {
      type: String,
      default: '前往第一模块'
    },
    align: {
      type: String,
      default: 'right',
      validator: (value) => ['center', 'right'].includes(value)
    },
    to: {
      type: String,
      default: '/first' // 默认跳转到/first
    }
  })
  
  const router = useRouter()
  const navigate = () => {
    router.go(props.to) // 使用动态路径
  }
</script>
  
<style scoped>
    .button-container {
    display: flex;
    align-items: center;
    margin: 2rem 0;
    /* justify-content 改为动态控制 */
    }
  
  .nav-button {
    padding: 24px 48px;
    background-color: var(--vp-c-brand);
    color: rgb(255, 255, 255);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 20px;
    font-weight: 600;
    transition: 
      background-color 0.3s,
      transform 0.2s,
      box-shadow 0.3s;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  @media (min-width: 768px) {
    .nav-button {
      font-size: 24px;
      padding: 32px 64px;
    }
  }
  @media (min-width: 768px) {
  .button-container {
    padding-right: 3rem;
  }
}
</style>