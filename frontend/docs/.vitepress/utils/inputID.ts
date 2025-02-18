import axios from 'axios';

// 创建用户的 API 请求
export const createUser = async (userID: string) => {
    try {
        // 请求后端创建用户
        const response = await axios.post('http://127.0.0.1:8000/ChatGPT/create_user/', { user_id: userID });
        return response.data; // 返回后端响应
    } catch (error) {
        console.error('Error creating user:', error);
        throw new Error('创建用户失败');
    }
};

// 弹出输入框并要求用户输入 ID
export const promptUserID = async (): Promise<string> => {
    const userEnteredID = prompt("请您填写您的手机尾号四位数(如:0817)");
    if (userEnteredID) {
        // 如果用户输入了ID，则创建用户
        await createUser(userEnteredID);
        return userEnteredID;
    } else {
        throw new Error('手机号后四位输入不正确');
    }
};
