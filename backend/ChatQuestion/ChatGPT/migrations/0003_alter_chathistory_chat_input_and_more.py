# Generated by Django 5.1.5 on 2025-03-01 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatGPT', '0002_chathistory_is_user_alter_chathistory_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chathistory',
            name='chat_input',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='chathistory',
            name='gpt_response',
            field=models.TextField(blank=True),
        ),
    ]
