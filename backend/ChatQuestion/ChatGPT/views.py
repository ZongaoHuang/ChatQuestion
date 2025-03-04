import uuid
import zipfile
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, StreamingHttpResponse


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
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        prompt = data.get('prompt')
        session_id = data.get('session_id', str(uuid.uuid4())[:8])  # 生成简短会话ID
        
        # 验证用户存在
        if not User.objects.filter(user_id=user_id).exists():
            return JsonResponse({'error': '用户不存在'}, status=400)
            
        response = ark_chat(prompt, user_id, session_id)
        return JsonResponse({'response': response})

# 保存聊天记录
# 修改保存聊天记录接口
@csrf_exempt
def save_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            messages = data.get("messages")
            session_id = data.get("session_id", "default")
            if not user_id or not messages:
                return JsonResponse({"error": "Missing required parameters"}, status=400)

            user = User.objects.get(user_id=user_id)
            
            chat_records = []
            for msg in messages:
                # 用户消息只保存 chat_input
                if msg.get("is_user"):
                    chat_records.append(ChatHistory(
                        user=user,
                        session_id=session_id,  # 这里接收前端传来的session_id
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
            if stage == 1 or 4:  # 第一阶段，包含聊天记录
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
            if stage == 1 or 4: 
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
            report_link = f"/reports/{report_filename}"

            # 更新用户模型中的报告链接字段
            if stage == 1 or 3:
                user.report_stage_1_link = report_link
            elif stage == 2 or 4:
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

from django.http import FileResponse
from django.conf import settings
import os

def report_list(request):
    """获取全部报告列表"""
    try:
        report_dir = settings.MEDIA_ROOT
        
        all_files = [
            f for f in os.listdir(report_dir) 
            if f.endswith('.json')
        ]
        
        reports = []
        for filename in all_files:
            file_path = os.path.join(report_dir, filename)
            stats = os.stat(file_path)
            reports.append({
                "name": filename,
                "size": stats.st_size,
                "created": stats.st_ctime
            })
            
        return JsonResponse({"reports": reports})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
import tempfile  # 新增导入
def download_all_reports(request):
    """打包下载全部报告（修复版）"""
    try:
        report_dir = settings.MEDIA_ROOT
        zip_filename = f"reports_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"

        def file_generator():
            # 使用临时文件缓冲
            with tempfile.SpooledTemporaryFile() as tmp:
                with zipfile.ZipFile(tmp, 'w') as zipf:
                    for filename in os.listdir(report_dir):
                        if not filename.endswith('.json') or '/' in filename:
                            continue
                        file_path = os.path.join(report_dir, filename)
                        zipf.write(file_path, arcname=filename)
                
                # 重置文件指针并读取内容
                tmp.seek(0)
                while chunk := tmp.read(4096):
                    yield chunk

        response = StreamingHttpResponse(
            file_generator(),
            content_type='application/zip'
        )
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)