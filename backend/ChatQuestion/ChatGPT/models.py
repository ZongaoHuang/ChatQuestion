from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)  # 使用当前中国时间
    report_stage_1_link = models.URLField(blank=True, null=True)  # 阶段 1 报告链接
    report_stage_2_link = models.URLField(blank=True, null=True)  # 阶段 2 报告链接

    def __str__(self):
        return self.user_id

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_input = models.TextField()
    gpt_response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # 使用当前中国时间

    def __str__(self):
        return f"Chat with {self.user.user_id} at {self.created_at}"

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.IntegerField()  # 阶段 1 或 2
    user_input = models.TextField()
    report_link = models.URLField(blank=True, null=True)  # 保存报告位置链接
    time_spent = models.IntegerField()  # 花费的时间，单位为秒
    created_at = models.DateTimeField(default=timezone.now)  # 使用当前中国时间

    def __str__(self):
        return f"Report for {self.user.user_id} at stage {self.stage}"
