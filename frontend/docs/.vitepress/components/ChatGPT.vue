<script setup>
import { ref, defineProps, onMounted } from 'vue';
import { generateChat, DEFAULT_CHAT, TITLE, sumitFirstStageReport, submitSecondStageReport } from '../utils/openai.ts';

const props = defineProps({
  userID: {
    type: String,
    required: true
  }
});

const chat = ref(DEFAULT_CHAT);  // ChatGPT 交互的内容
const userInput = ref('');       // 用户通过输入框输入的内容
const loading = ref(false);
const stage = ref(1);            // 当前阶段，1是第一阶段，2是第二阶段
const timeLeft = ref(600);       // 10分钟，单位是秒
const timer = ref(null);         // 用于计时器
const isSubmitDisabled = ref(false); // 控制提交按钮是否禁用
// 格式化时间为 “X分 Y秒”
const formatTime = (timeInSeconds) => {
  const minutes = Math.floor(timeInSeconds / 60);
  const seconds = timeInSeconds % 60;
  return `${minutes}分${seconds}秒`;
};

// 进入下一阶段：第一阶段结束后
const nextStage = async () => {
  if (stage.value === 1) {
    clearInterval(timer.value); // 停止当前计时器
    const timeSpent = 600 - timeLeft.value; // 第一阶段已用时间
    await sumitFirstStageReport(props.userID, userInput.value, timeSpent); // 保存第一阶段报告
    stage.value = 2;            // 切换到第二阶段
    timeLeft.value = 600;       // 重置计时器为10分钟
    startTimer();               // 重新启动计时器
  }
};

const commit = async () => {
  if (window.confirm('点击确定后无法更改答案')) {
    clearInterval(timer.value); // 停止计时器
    const timeSpent = 600 - timeLeft.value; // 第二阶段已用时间
    await submitSecondStageReport(props.userID, userInput.value, timeSpent); // 保存第二阶段报告
    alert('报告已提交');
    isSubmitDisabled.value = true; // 禁用提交按钮
  }
};
// 计时器函数：每秒更新一次
const startTimer = () => {
  timer.value = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--;
    } else {
      clearInterval(timer.value);
      if (stage.value === 1) {
        nextStage(); // 第一阶段时间到，自动进入下一阶段
      } else if (stage.value === 2) {
        commit();    // 第二阶段时间到，自动提交报告
      }
    }
  }, 1000);
};

// 进入下一阶段的按钮，第一次进入时启动计时
onMounted(() => {
  startTimer();
});

// 发送请求，与 ChatGPT 交互（仅适用于第一阶段）
const send = async () => {
  loading.value = true;
  chat.value = await generateChat(chat.value, props.userID);
  loading.value = false;
};

const input1 = ({ target }) => {
  chat.value = target.value;
};

const input2 = ({ target }) => {
  userInput.value = target.value;
};

const reset = () => {
  chat.value = TITLE;
};
</script>

<template>
    
    <div class="chat-container">
        <!-- 输入框部分 -->
        <div class="timer">
            剩余时间: {{ formatTime(timeLeft) }}
        </div>
        <div v-if="stage === 1">
            <h2>ChatGPT</h2>
            <textarea
                :value="chat"
                @input="input1"
                placeholder="请输入消息..."
                class="chat-input"
            ></textarea>
            
            <!-- loading 动画 -->
            <div v-if="loading" class="loading"></div>

            <!-- 工具栏 -->
            <div class="toolbar">
                <span class="letters">{{ chat.length || 0 }}</span>
                <button @click="send" class="send">发送消息</button>
                <button @click="reset" class="reset">一键复制题目</button>
            </div>
        </div>
        <br></br>
        <!-- 计时器显示 -->
        <div v-if="stage === 1">
            <h3>创意产生</h3>
            首先，请您先构思出若干条初步的创意点子。这一阶段的想法生成时间为10分钟，10分钟内，请将您的初步创意点子写入到文本框中。  
        </div>
        <div v-if="stage === 2">
            <h3>创意细化</h3>
            接下来，ChatGPT工具将会消失，请您对前一个阶段生成的初步创意和想法进行筛选、细化与完善。这一阶段的方案完善时间为10分钟，10分钟内，请将最终创意方案填写入到文本框中。
        </div>
        <textarea
            :value="userInput"
            @input="input2"
            placeholder="请输入消息..."
            class="user-input"
            ></textarea>

            <div class="toolbar">
                <span class="letters">{{ userInput.length || 0 }}</span>
                <button @click="nextStage" class="next" v-if="stage === 1">进入创意细化阶段</button>
                <button @click="commit" class="commit" v-if="stage === 2" :disabled="isSubmitDisabled">提交</button>
            </div>
            <br></br>
    </div>

    
</template>


<style scoped>
/* prettier-ignore */

.timer {
    font-size: 18px;
    color: #ff0000;
    margin-top: 10px;
    font-weight: bold;
  }
.loading {
    position: absolute;
    left: 50%;
    top: 50%;
    margin-left: -8px;
    margin-top: -8px;
    width: 3px;
    height: 3px;
    border-radius: 100%; /* 圆角 */
    box-shadow: 
    0 -10px 0 1px #00a0e8, /* 上, 1px 扩展 */ 
    0 10px #00a0e8, /* 下 */ 
    -10px 0 #00a0e8, /* 左 */
    10px 0 #00a0e8, /* 右 */ 
    -7px -7px 0 0.5px #00a0e8, /* 左上, 0.5px扩展 */
    7px -7px 0 1.5px #00a0e8, /* 右上, 1.5px扩展 */
    7px 7px #00a0e8,/* 右下 */
    -7px 7px #00a0e8; /* 左下 */
}
.spin {
    animation: spin 1s steps(8) infinite;
}
@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
.wrapper {
    position: relative;
}
textarea {
    width: 100%;
    height: calc(100vh - 600px);
    min-height: 300px;
    padding: 18px;
    margin-top: 10px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
    font-size: 14px;
    background-color: var(--vp-c-bg);
    color: var(--vp-c-text-1);
}
textarea:focus {
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.15);
}
.toolbar {
    text-align: right;
    padding-top: 5px;
    margin-bottom: -50px;
}
.letters {
    float: left;
    font-size: 14px;
    color: var(--vp-c-text-2);
    background-color: var(--vp-c-divider);
    border-radius: 8px;
    padding: 0 12px;
}
button {
    margin-left: 12px;
    line-height: 36px;
    font-size: 16px;
    padding: 0 0.8em;
    color: var(--vp-c-text-1);
    border-radius: 8px;
    background-color: var(--vp-c-divider);
    user-select: none;
}
button.send {
    color: var(--vp-c-text-inverse-1);
    background-color: var(--vp-c-brand);
}
.VPDocFooter {
    margin-top: 20px;
}
</style>
