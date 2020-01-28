from __future__ import absolute_import
from celery.decorators import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import time
from django.core.mail import send_mail
from django.conf import settings

import competition.models as com_model
from django.core.exceptions import ObjectDoesNotExist
import logging


# 异步任务
@task
def send_email_demo(user, subject, message):
	to_who = user.email
	from_who = settings.EMAIL_FROM  # 发件人  已经写在 配置中了 直接型配置中获取
	# meg_html = '<a href="http://www.baidu.com">点击跳转</a>'  # 发送的是一个html消息 需要指定
	send_mail(subject, message, from_who, [to_who])
	return True

