<template>
    <div v-if="timerRunning" class="timer">
      Time remaining: {{ remainingTime }} seconds
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue';
  
  const remainingTime = ref(600);
  const timerRunning = ref(true);
  
  watch(remainingTime, (newTime) => {
    if (newTime <= 0) {
      timerRunning.value = false;
    }
  });
  
  const updateTime = (time) => {
    remainingTime.value = time;
  };
  
  </script>
  
  <style scoped>
  .timer {
    font-size: 18px;
    color: red;
    margin-top: 1rem;
  }
  </style>
  