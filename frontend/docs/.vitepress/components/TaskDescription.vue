<template>
    <div class="task-description">
      <h2>Task Description:</h2>
      <p>Please read the following task description carefully and answer accordingly:</p>
      <p>{{ taskContent }}</p>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue';
  
  const props = defineProps({
    taskContent: String
  });
  </script>
  
  <style scoped>
  .task-description {
    margin-top: 2rem;
    font-size: 16px;
  }
  </style>
  