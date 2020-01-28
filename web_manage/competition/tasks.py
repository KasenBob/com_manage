from __future__ import absolute_import
from celery.decorators import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import time
from django.core.cache import cache
from . import models
import all.models as all_model
import student.models as student_model
import teacher.models as teacher_model


@periodic_task(run_every=crontab(minute=0, hour=0))
def update_com_status():
	com_list = models.com_basic_info.objects.all()
	for com in com_list:
		if com.com_status != '3':
			com.update_status()
	return True


@periodic_task(run_every=crontab(minute=10, hour=0))
def update_group_status():
	com_list = models.com_basic_info.objects.filter(com_status='1')
	for com in com_list:
		group_list = models.com_group_basic_info.objects.filter(com_id=com, status='0')
		for group in group_list:
			#print(group)
			com_stu_list = student_model.com_stu_info.objects.filter(group_id=group.group_id)
			com_teach_list = teacher_model.com_teach_info.objects.filter(group_id=group.group_id)
			flag = 1
			# 判断学生是否全部确认
			for com_stu in com_stu_list:
				if com_stu.status == '0':
					flag = 0
					break
			# 若学生全部确认则报名成功
			if flag == 1:
				for com_teach in com_teach_list:
					com_teach.status = '1'
					com_teach.save()
				group.status = '1'
				group.save()
			# 若有学生未确认则报名失败
			else:
				for com_stu in com_stu_list:
					com_stu.delete()
				for com_teach in com_teach_list:
					com_teach.delete()
				group.delete()
