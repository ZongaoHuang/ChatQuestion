from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# chat/services_openai.py

# chat/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import ark_chat
from .models import User, ChatHistory, Report
import os
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import localtime

# 创建用户
@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            if not user_id:
                return JsonResponse({"error": "用户ID不能为空"}, status=400)
            user, created = User.objects.get_or_create(user_id=user_id)
            return JsonResponse({"message": "用户创建成功" if created else "用户已存在"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "仅支持POST方法"}, status=405)


@csrf_exempt  # 示例中关闭 CSRF 校验（生产环境请注意安全配置）
def chat_view(request):
    """
    接收 POST 请求，提取请求体中的 'words' 参数，
    调用方舟平台模型服务后将生成的回答作为 JSON 响应返回。
    """
    if request.method != 'POST':
        return JsonResponse({'error': '只支持 POST 方法'}, status=405)
    
    try:
        data = json.loads(request.body)
        prompt = data.get('words', '')
    except Exception:
        return JsonResponse({'error': '请求体不是合法的 JSON'}, status=400)
    
    if not prompt:
        return JsonResponse({'error': '缺少参数 words'}, status=400)
    
    answer = ark_chat(prompt)
    return JsonResponse({'response': answer})

# 保存聊天记录
# 修改保存聊天记录接口
@csrf_exempt
def save_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            messages = data.get("messages")
            
            if not user_id or not messages:
                return JsonResponse({"error": "Missing required parameters"}, status=400)

            user = User.objects.get(user_id=user_id)
            
            chat_records = []
            for msg in messages:
                # 用户消息只保存 chat_input
                if msg.get("is_user"):
                    chat_records.append(ChatHistory(
                        user=user,
                        chat_input=msg.get("content", ""),
                        gpt_response="",  # 用户消息清空响应字段
                        is_user=True
                    ))
                else:
                    chat_records.append(ChatHistory(
                        user=user,
                        chat_input="",  # GPT消息清空输入字段
                        gpt_response=msg.get("content", ""),
                        is_user=False
                    ))
            
            ChatHistory.objects.bulk_create(chat_records)
            return JsonResponse({"message": "Chat history saved successfully"})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
def get_chat_history(request):
    if request.method == "GET":
        try:
            user_id = request.GET.get("user_id")
            if not user_id:
                return JsonResponse({"error": "缺少用户ID"}, status=400)
                
            user = User.objects.get(user_id=user_id)
            history = ChatHistory.objects.filter(user=user).order_by('created_at')
            
            return JsonResponse({
                "history": [
                    {
                        # 修正内容映射逻辑
                        "content": record.gpt_response if not record.is_user else record.chat_input,
                        "is_user": record.is_user,
                        "timestamp": int(record.created_at.timestamp()),
                        "response": record.gpt_response  # 保留原始字段
                    }
                    for record in history
                    # 过滤占位符
                    if (record.is_user and record.chat_input not in ["[USER_MESSAGE]", ""]) 
                    or (not record.is_user and record.gpt_response not in ["[SYSTEM_QUERY]", ""])
                ]
            })
            
        except User.DoesNotExist:
            return JsonResponse({"error": "用户不存在"}, status=404)

# 保存报告
@csrf_exempt
def save_report(request):
    if request.method == "POST":
        try:
            # 获取请求中的数据
            data = json.loads(request.body)
            user_id = data.get("user_id")
            stage = data.get("stage")
            user_input = data.get("user_input")  # 用户输入的内容
            time_spent = data.get("time_spent")  # 阶段花费的时间

            if not user_id or not stage or not user_input or not time_spent:
                return JsonResponse({"error": "缺少必填参数"}, status=400)

            # 获取用户
            user = User.objects.get(user_id=user_id)

            # 获取该用户的所有聊天记录
            chat_history_content = []
            if stage == 1:  # 第一阶段，包含聊天记录
                chat_history = ChatHistory.objects.filter(user=user).order_by('created_at')
                chat_history_content = [
                    {
                        "chat_time": localtime(chat.created_at).strftime('%Y-%m-%d %H:%M:%S'),  # 转换为中国时间并格式化
                        "chat_input": chat.chat_input,
                        "gpt_response": chat.gpt_response
                    }
                    for chat in chat_history
                ]

            # 获取当前中国时间
            current_time = timezone.localtime(timezone.now())  # 获取北京时间
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if stage == 1: 
            # 创建报告内容
                report_data = {
                    "created_at": formatted_time,
                    "user_phone": user_id,
                    "stage": stage,
                    "chat_history": chat_history_content,  # 仅阶段1有聊天记录
                    "user_input": user_input,
                    "time_spent": time_spent
                }
            else:
                report_data = {
                    "created_at": formatted_time,
                    "user_phone": user_id,
                    "stage": stage,
                    "user_input": user_input,
                    "time_spent": time_spent
                }
            # 修改报告命名，使用 stage 来区分报告文件
            report_filename = f"report_{user_id}_stage{stage}_{current_time.strftime('%Y%m%d%H%M%S')}.json"
            report_file_path = os.path.join('reports', report_filename)

            # 确保报告文件夹存在
            os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

            # 使用 ensure_ascii=False 来确保中文字符被正确保存
            with open(report_file_path, 'w', encoding='utf-8') as report_file:
                json.dump(report_data, report_file, ensure_ascii=False, indent=4)

            # 创建报告链接
            report_link = f"http://127.0.0.1:8000/reports/{report_filename}"

            # 更新用户模型中的报告链接字段
            if stage == 1:
                user.report_stage_1_link = report_link
            elif stage == 2:
                user.report_stage_2_link = report_link
            user.save()

            # 创建报告记录
            Report.objects.create(
                user=user,
                stage=stage,
                user_input=user_input,
                report_link=report_link,
                time_spent=time_spent,
                created_at=current_time  # 使用中国时间
            )

            return JsonResponse({"message": "报告保存成功", "report_link": report_link})

        except User.DoesNotExist:
            return JsonResponse({"error": "用户不存在"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "仅支持POST方法"}, status=405)