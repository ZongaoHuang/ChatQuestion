import axios from 'axios';

export interface ChatMessage {
    content: string
    isUser: boolean
    timestamp: number
    sessionID: string  // 新增会话ID字段
}
  
// const baseURL = '/ChatGPT/'; // Removed baseURL to simplify, using relative paths directly
// 或者 const baseURL = 'http://localhost:8000';


export const DEFAULT_CHAT = '👨‍🎓Human:你叫什么名字？\n🤖ChatGPT:我叫ChatGPT，我是一个聊天机器人。\n👨‍🎓Human:';

// 使用模板字符串（反引号）定义多行文本
export const TITLE: string = `👨‍🎓Human:
任务描述请您阅读以下内容，按照要求完成以下手机壳创意文案设计任务。

您是苹果公司（iPhone）手机事业部的产品经理。目前，公司计划推出一款新的手机壳，你需要为该款手机壳创作广告文案。该广告将展示在抖音、小红书、微信朋友圈和微博等宣传平台上，考虑到用户在这些平台上的注意力持续时间较短，你需要尽可能地创作吸引眼球的创意文案。
以下是这款手机壳的产品详情：

**1. 产品名称：iPhone皮革翻盖手机壳**

**2. 产品详情与亮点**

- 材质方面：采用最优质的复古PU皮革和柔软TPU材质，具备无与伦比的强度和耐用性，清洁时只需用湿布擦拭灰尘和污垢即可。
- 外部设计方面：得益于创新设计，拥有内置支架和豪华卡夹口袋，提供360度全方位保护，边缘凸起确保相机和屏幕得到最大程度保护。防刮耐磨，告别指纹和划痕，内部柔软防滑衬里提供超强缓冲回弹，保护手机免受磨损。
- 支架功能方面：内置支架模式可实现免提观看视频或与朋友聊天，非常适合多任务处理。
- 兼容性方面：精准适配多种iPhone型号，可无障碍访问所有端口、控制按键和传感器。
- 价格：原价60元；促销价30元（五折），免运费。

**3.任务要求**

  请您考虑创意的新颖性和实用性，给出**200字**以上的创意方案。

- 内容新颖性：创作的广告文案内容要突出产品上述特点与优势，能够吸引消费者购买。
- 创意实用性：文案展示位置需适应抖音、小红书、微信朋友圈和微博这些社交平台的展示特点，在短时间内吸引用户注意力。`;



  
export const generateChat = async (
    message: string, 
    userID: string,
    sessionID: string = 'default'
): Promise<ChatMessage> => {
    try {
        const res = await axios.post('/api/ChatGPT/chat/', {
            user_id: userID,
            prompt: message,
            session_id: sessionID
        });

        if (res?.data?.response) {
            // 保存时包含 sessionID
            const newMessage: ChatMessage = {
                content: message,
                isUser: true,
                timestamp: Date.now(),
                sessionID: sessionID
            };
            
            const botMessage: ChatMessage = {
                content: res.data.response,
                isUser: false,
                timestamp: Date.now(),
                sessionID: sessionID
            };

            await saveChatHistory(userID, [newMessage, botMessage]);
            
            return botMessage;
        }
        
        return {
            content: '请求失败，请重试',
            isUser: false,
            timestamp: Date.now(),
            sessionID: sessionID
        };
    } catch (error) {
        console.error('Error generating chat:', error);
        return {
            content: '请求异常，请检查网络',
            isUser: false,
            timestamp: Date.now(),
            sessionID: sessionID
        };
    }
};

export const saveChatHistory = async (userID: string, messages: ChatMessage[]) => {
try {
    await axios.post('/api/ChatGPT/save_chat/', {
    user_id: userID,
    messages: messages.map(msg => ({
        content: msg.content,
        is_user: msg.isUser,
        timestamp: msg.timestamp,
        session_id: msg.sessionID  // 传递会话ID
    }))
    });
} catch (error) {
    console.error('Error saving chat history:', error);
}
};

// 新增获取聊天记录方法
export const getChatHistory = async (userID: string): Promise<ChatMessage[]> => {
try {
    const response = await axios.get('/api/ChatGPT/get_chat_history/', {
    params: { user_id: userID }
    });
    
    return response.data.history.map((item: any) => ({
    content: item.content,
    isUser: item.is_user,
    timestamp: item.timestamp * 1000 // 转换为毫秒
    }));
    
} catch (error) {
    console.error('Error fetching chat history:', error);
    return [];
}
};
// 提交系统A的第一阶段报告
export const submitFirstStageReport_A = async (userID: string, userInput: string, timeSpent: number) => {
    try {
        const reportData = {
            user_id: userID,
            stage: 1,
            user_input: userInput,
            time_spent: timeSpent // 假设10分钟，后续会更新为动态计算的时间
        };
        await axios.post('/api/ChatGPT/save_report/', reportData);
    } catch (error) {
        console.error('Error saving report:', error);
    }
};

// 提交系统A的第二阶段报告
export const submitSecondStageReport_A = async (userID: string, userInput: string, timeSpent: number) => {
    try {
        const reportData = {
            user_id: userID,
            stage: 2,
            user_input: userInput,
            time_spent: timeSpent // 假设10分钟，后续会更新为动态计算的时间
        };
        await axios.post('/api/ChatGPT/save_report/', reportData);
    } catch (error) {
        console.error('Error submitting second stage report:', error);
    }
};



// 提交系统B的第一阶段报告
export const submitFirstStageReport_B = async (userID: string, userInput: string, timeSpent: number) => {
    try {
        const reportData = {
            user_id: userID,
            stage: 3,
            user_input: userInput,
            time_spent: timeSpent // 假设10分钟，后续会更新为动态计算的时间
        };
        await axios.post('/api/ChatGPT/save_report/', reportData);
    } catch (error) {
        console.error('Error submitting second stage report:', error);
    }
};

// 提交系统B的第二阶段报告
export const submitSecondStageReport_B = async (userID: string, userInput: string, timeSpent: number) => {
    try {
        const reportData = {
            user_id: userID,
            stage: 4,
            user_input: userInput,
            time_spent: timeSpent // 假设10分钟，后续会更新为动态计算的时间
        };
        await axios.post('/api/ChatGPT/save_report/', reportData);
    } catch (error) {
        console.error('Error saving report:', error);
    }
};