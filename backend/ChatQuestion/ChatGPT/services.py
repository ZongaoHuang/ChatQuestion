# chat/services_openai.py

from django.conf import settings
from django.db import models  # 新增聚合函数需要
from .models import ChatHistory, User  # 确保相对导入正确
from openai import OpenAI  # 修正客户端导入
client = OpenAI(
    api_key = getattr(settings, "ARK_API_KEY1", None),
    base_url  = getattr(settings, "ARK_BASE_URL1", "https://api.chatanywhere.tech/v1")
    )

def ark_chat1(prompt: str) -> str:
    """
    使用 OpenAI SDK 调用方舟平台模型服务，传入 prompt，返回生成的回答文本。
    """
    api_key = getattr(settings, "ARK_API_KEY", None)
    endpoint_id = getattr(settings, "ARK_ENDPOINT_ID", None)
    base_url = getattr(settings, "ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    if not api_key or not endpoint_id:
        return "请在 settings 中配置 ARK_API_KEY 和 ARK_ENDPOINT_ID"
    
    # 配置 OpenAI SDK
    client = OpenAI(
        # 从环境变量中读取您的方舟API Key
        api_key=api_key, 
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
    try:
        completion = client.chat.completions.create(
            model=endpoint_id,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # OpenAI SDK 返回的 message 为字典，取出其中的 content 字段
        return completion.choices[0].message.content
    except Exception as e:
        return f"请求错误: {str(e)}"

# 调用OPEN AI ChatGPT服务
# 调用OPEN AI ChatGPT服务
def ark_chat(prompt: str, user_id: str, session_id: str = 'default') -> str:
    """带上下文保存的GPT调用"""
    try:
        # 获取最近5条历史记录
        history = ChatHistory.objects.filter(
            user__user_id=user_id,
            session_id=session_id
        ).order_by('-sequence')[:5]
        
        # 构建消息列表（按时间正序）
        messages = []
        for h in reversed(history):
            role = "user" if h.is_user else "assistant"
            messages.append({"role": role, "content": h.chat_input or h.gpt_response})
        
        messages.append({"role": "user", "content": prompt})
        
        # 调用GPT
        completion = client.chat.completions.create(
            model="gpt-4o-mini-ca",
            messages=messages,
            temperature=0.7
        )
        
        # 保存对话记录
        max_seq = ChatHistory.objects.filter(
            user__user_id=user_id,
            session_id=session_id
        ).aggregate(models.Max('sequence'))['sequence__max'] or 0
        
        ChatHistory.objects.bulk_create([
            ChatHistory(
                user=User.objects.get(user_id=user_id),
                chat_input=prompt,
                is_user=True,
                session_id=session_id,
                sequence=max_seq + 1
            ),
            ChatHistory(
                user=User.objects.get(user_id=user_id),
                gpt_response=completion.choices[0].message.content,
                session_id=session_id,
                sequence=max_seq + 2
            )
        ])
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"请求失败: {str(e)}"