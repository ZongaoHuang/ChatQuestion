from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.CharField(max_length=255, unique=True) #  手机号后四位
    created_at = models.DateTimeField(default=timezone.now)  # 使用当前中国时间
    report_stage_1_link = models.URLField(blank=True, null=True)  # 阶段 1 报告链接
    report_stage_2_link = models.URLField(blank=True, null=True)  # 阶段 2 报告链接

    def __str__(self):
        return self.user_id

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_input = models.TextField(blank=True)
    gpt_response = models.TextField(blank=True)
    is_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=32, default='default')  # 新增会话ID
    sequence = models.IntegerField(default=0)  # 新增消息顺序

    def save(self, *args, **kwargs):
        # 自动清理无效数据
        if self.is_user:
            self.gpt_response = ""  # 用户消息清空响应字段
        else:
            self.chat_input = ""    # AI消息清空输入字段
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['sequence']  # 确保按顺序获取

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.IntegerField()  # 阶段 1 或 2
    user_input = models.TextField()
    report_link = models.URLField(blank=True, null=True)  # 保存报告位置链接
    time_spent = models.IntegerField()  # 花费的时间，单位为秒
    created_at = models.DateTimeField(default=timezone.now)  # 使用当前中国时间

    def __str__(self):
        return f"Report for {self.user.user_id} at stage {self.stage}"
