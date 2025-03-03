<script lang="ts" setup >
import { ref, defineProps, onMounted, onUnmounted} from 'vue';
import { generateChat, DEFAULT_CHAT, TITLE, submitFirstStageReport_B, submitSecondStageReport_B, getChatHistory} from '../utils/openai.ts';
import { useRouter } from 'vitepress'
import type { ChatMessage } from '../utils/openai.ts'; // 单独导入类型
// 添加 messages 声明
const messages = ref<ChatMessage[]>([])
// 在setup部分添加路由
const router = useRouter()
const props = defineProps({
  userID: {
    type: String,
    required: true
  }
});

const chat = ref(DEFAULT_CHAT);  // ChatGPT 交互的内容
const chatInput = ref('');       // 用户对ChatGPT的提问
const userInput1 = ref('');       // 用户第一阶段通过输入框输入的内容
const userInput2 = ref('');       // 用户第二阶段通过输入框输入的内容
const loading = ref(false);
const timerActive = ref(false);
const stage = ref(3);            // 当前阶段，3是系统B的第一阶段，4是系统B的第二阶段
const timeLeft = ref(600);       // 10分钟，单位是秒
const timer = ref(null);         // 用于计时器
const isSubmitDisabled = ref(false); // 控制提交按钮是否禁用
// 格式化时间为 “X分 Y秒”
const formatTime = (timeInSeconds) => {
  const minutes = Math.floor(timeInSeconds / 60);
  const seconds = timeInSeconds % 60;
  return `${minutes}分${seconds}秒`;
};

// 改进的阶段切换
const nextStage = async () => {
  if (stage.value !== 3) return;
  
  stopTimer();
  const timeSpent = 600 - timeLeft.value;
  await submitFirstStageReport_B(props.userID, userInput1.value, timeSpent);
  
  // 原子化状态更新
  stage.value = 4;
  timeLeft.value = 600;
  
  startTimer();
};

const commit = async () => {
  if (window.confirm('点击确定后无法更改答案')) {
    clearInterval(timer.value); // 停止计时器
    const timeSpent = 600 - timeLeft.value; // 第二阶段已用时间
    await submitSecondStageReport_B(props.userID, userInput2.value, timeSpent); // 保存第二阶段报告
    alert('报告已提交');
    isSubmitDisabled.value = true; // 禁用提交按钮
    router.go('/third')

    
  }
};
// 改进的计时器控制
const startTimer = () => {
  // 确保先清除旧计时器
  stopTimer();
  
  timerActive.value = true;
  const startTime = Date.now();
  const expectedEndTime = startTime + timeLeft.value * 1000;

  const tick = () => {
    if (!timerActive.value) return;

    const currentTime = Date.now();
    const elapsed = currentTime - startTime;
    timeLeft.value = Math.ceil((expectedEndTime - currentTime) / 1000);

    if (currentTime >= expectedEndTime) {
      handleTimeout();
    } else {
      timer.value = setTimeout(tick, Math.max(0, (expectedEndTime - currentTime) % 1000));
    }
  };

  tick();
};
// 统一超时处理
const handleTimeout = () => {
  stopTimer();
  if (stage.value === 3) {
    nextStage();
  } else {
    commit();
  }
};
// 安全的计时器停止
const stopTimer = () => {
  timerActive.value = false;
  if (timer.value) {
    clearTimeout(timer.value);
    timer.value = null;
  }
};
// 进入下一阶段的按钮，第一次进入时启动计时
// 初始化时加载历史记录


// 发送请求，与 ChatGPT 交互（仅适用于第二阶段）
// 修改后的send方法
const send = async () => {
  if (!chatInput.value.trim()) return;
  
  const userMessage = {
    content: chatInput.value,
    isUser: true,
    timestamp: Date.now()
  };
  
  messages.value.push(userMessage);
  
  try {
    const response = await generateChat(chatInput.value, props.userID);
    messages.value.push(response);
  } catch (error) {
    messages.value.push({
      content: '请求失败，请稍后重试',
      isUser: false,
      timestamp: Date.now()
    });
  }
  
  chatInput.value = '';
};

const input1 = ({ target }) => {
  chat.value = target.value;
};

const input2 = ({ target }) => {
  userInput1.value = target.value;
};

const input3 = ({ target }) => {
  userInput2.value = target.value;
};
const reset = () => {
  chat.value = TITLE;
};
const countNonWhitespaceChars = (text) => {
  return text.replace(/\s/g, '').length;
};

onMounted(async () => {
  startTimer();
  //加入停顿
  await new Promise((resolve) => setTimeout(resolve, 1000));
  messages.value = await getChatHistory(props.userID);
});
// 组件卸载时清理
onUnmounted(stopTimer);
</script>

<template>
    
    <div class="chat-container">
        <!-- 输入框部分 -->

        <div v-if="stage === 3">
            <br></br>
            <h2>创意产生</h2>
            <div class="timer">
              剩余时间: {{ Math.floor(timeLeft / 60) }}分{{ timeLeft % 60 }}秒
            </div>
            <br>
            首先，请您先构思出若干条初步的创意点子。这一阶段的想法生成时间为10分钟，10分钟内，请将您的初步创意点子填写在下方文本框中。
            
            <strong>请注意：在这一过程中请不要使用任何搜索引擎和生成式AI等工具。</strong>
            <textarea
            :value="userInput1"
            @input="input2"
            placeholder="请输入消息..."
            class="user-input"
            ></textarea>

            <div class="toolbar">
                <span class="letters">{{ countNonWhitespaceChars(userInput1) }}</span>
                <button @click="nextStage" class="next" v-if="stage === 3">进入创意细化阶段</button>
            </div>  
        </div>
        
        <br></br>
        <!-- 计时器显示 -->
        <div v-if="stage === 4">
            <h2>创意产生</h2>
            这是你在上一个10分钟内，进行初步创意的点子，你可以进行参照。
            <textarea
            :value="userInput1"
            @input="input2"
            placeholder="请输入消息..."
            class="user-input"
            ></textarea>
            <br>

            <h2>ChatGPT</h2>
            <!-- 聊天面板 -->
            <div class="chat-panel">
              <div class="message-list">
                <div 
                  v-for="(msg, index) in messages"
                  :key="index"
                  :class="['message-bubble', { 'user-message': msg.isUser, 'gpt-message': !msg.isUser }]"
                >
                  <div class="message-content">{{ msg.content }}</div>
                  <div class="message-time">{{ new Date(msg.timestamp).toLocaleTimeString() }}</div>
                </div>
              </div>
              
              <!-- 输入区域 -->
              <div class="input-area">
                <textarea
                  class="chat-input-area"
                  v-model="chatInput"
                  placeholder="输入您的问题..."
                  @keydown.enter.prevent="send"
                ></textarea>
                <button @click="send">发送</button>
              </div>
            </div>

            <h2>创意细化</h2>
            <div class="timer">
              剩余时间: {{ Math.floor(timeLeft / 60) }}分{{ timeLeft % 60 }}秒
            </div>
            <br>
            接下来，请您对前一个阶段生成的初步创意和想法进行筛选、细化与完善。这一阶段的方案完善时间为10分钟，10分钟内，请将最终创意方案填写在下方文本框中。
            <strong>请注意：在这一阶段您可以与本页面提供的“chatGPT”工具进行互动，以获得帮助。</strong>
            <textarea
            :value="userInput2"
            @input="input3"
            placeholder="请输入消息..."
            class="user-input"
            ></textarea>

            <div class="toolbar">
                <span class="letters">{{ countNonWhitespaceChars(userInput2) }}</span>
                <button @click="commit" class="commit" v-if="stage === 4" :disabled="isSubmitDisabled">提交</button>
            </div>
          </div>


            <br></br>
    </div>

    
</template>


<style scoped>
/* prettier-ignore */
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 80vh;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  overflow: hidden;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: var(--vp-c-bg-soft);
}

.message-bubble {
  max-width: 70%;
  margin: 0.5rem;
  padding: 1rem;
  border-radius: 12px;
  animation: fadeIn 0.3s ease;
}

.gpt-message {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  margin-right: auto;
}

.user-message {
  background: var(--vp-c-brand);
  color: white;
  margin-left: auto;
}

.message-content {
  word-break: break-word;
}

.message-time {
  font-size: 0.8rem;
  opacity: 0.7;
  margin-top: 0.5rem;
}

.input-area {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--vp-c-divider);
  textarea {
    flex: 1;
    max-height: 177px;
    min-height: 100px;
    padding: 0.8rem;
  }
  
  button {
    align-self: flex-end;
    padding: 0.8rem 1.5rem;
  }
  
}


@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
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
    margin-left: 24px;
    line-height: 48px;
    font-size: 16px;
    padding: 0 0.8em;
    color: var(--vp-c-text-1);
    border-radius: 8px;
    background-color: var(--vp-c-divider);
    user-select: none;
}
button.send {
    color: var(--vp-c-text-inverse-1);
}
button.commit {
    color: var(--vp-c-text-inverse-1);
    background-color:#00a0e8
}
.VPDocFooter {
    margin-top: 20px;
}

</style>
