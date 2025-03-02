# chat/services_openai.py

from django.conf import settings
from openai import OpenAI

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
def ark_chat(prompt: str) -> str:
    """
    使用第三方ChatGPT服务（chatanywhere.tech）获取回答
    """
    api_key = getattr(settings, "ARK_API_KEY1", None)
    base_url = getattr(settings, "ARK_BASE_URL1", None)
    
    if not api_key or not base_url:
        return "请在 settings 中配置 ARK_API_KEY1 和 ARK_BASE_URL1"

    try:
        # 创建独立客户端实例
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini-ca",  # 直接指定模型名称
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # 控制生成随机性
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"ChatGPT请求失败: {str(e)}"
