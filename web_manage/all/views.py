from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
import datetime
from . import models
import student.models as student_model
import teacher.models as teacher_model
import news.models  as news_model
import competition.models as com_model
from .tasks import send_email_demo
from .forms import ArticleForm
import os
from django.core.cache import cache
import time
from django.core import serializers
import json


# Create your views here.
def home(request):
	'''
	if request.session.get('is_login', None):
		if request.session.get('user_power', None) == '0':
			student = get_object_or_404(student_model.stu_basic_info,
			                            stu_number=request.session.get('user_number', None))
			subject = '登录通知'
			message = '您已登录'
			print(student)
		send_email_demo(student, subject, message)
	'''
	context = {}
	# sendmail.delay('test@test.com')
	'''
	# 学生需要储存信息
	if request.session['user_power'] == '0':
		all_inform_list = student_model.stu_inform.objects.filter(
			Recipient_acc=request.session['user_number']).order_by('-create_time')
		if len(all_inform_list) > 4:
			request.session['inform_list'] = all_inform_list[:5]
		else:
			request.session['inform_list'] = all_inform_list
	'''

	# 新闻列表
	key_1 = 'news_list'
	if cache.has_key(key_1):
		new_list = cache.get(key_1)
	else:
		new_list = news_model.news.objects.all().order_by('-created_time')
	cache.set(key_1, new_list, 30 * 60)
	i = 0
	news_list = []
	top_new = None
	for new in new_list:
		if i == 0:
			top_new = new
		elif i < 10:
			news_list.append(new)
		i += 1
	context['top_new'] = top_new
	context['news_list'] = news_list

	# 通知列表
	key_2 = 'inform_list'
	if cache.has_key(key_2):
		inform_list = cache.get(key_2)
	else:
		inform_list = models.inform.objects.all().order_by('-create_time')
	cache.set(key_2, inform_list, 30 * 60)
	i = 0
	informs_list = []
	for form in inform_list:
		if i < 10:
			informs_list.append(form)
		i += 1
	context['informs_list'] = informs_list

	# 正在进行比赛
	key_3 = 'com_list'
	if cache.has_key(key_3):
		com_list = cache.get(key_3)
	else:
		com_list = com_model.com_basic_info.objects.filter(com_status='0').order_by('-begin_regit')
	cache.set(key_3, com_list, 30 * 60)
	i = 0
	show_com_list = []
	for com in com_list:
		if i < 4:
			show_com_list.append(com)
		i += 1
	context['show_com_list'] = show_com_list

	return render(request, 'home/home.html', context)


# 登录
def login(request):
	context = {}
	if request.session.get('is_login', None):
		return redirect('/home')

	if request.method == "POST":
		t_account = request.POST.get('username', None)
		t_psword = request.POST.get('password', None)
		context = {}
		message = "请填写正确的账号和密码！"
		if t_account == "":
			context['message'] = "请输入账号！"
			return render(request, 'home/login.html', context)
		if t_psword == "":
			context['message'] = "请输入密码！"
			return render(request, 'home/login.html', context)
		if t_account and t_psword:
			t_account = t_account.strip()
			try:
				user = get_object_or_404(models.user_login_info, account=t_account)
				# 权限说明（学生：0; 指导老师：1; 竞赛委员：5;）
				if user.psword == t_psword:
					request.session['is_login'] = True
					request.session['user_number'] = user.account
					request.session['user_power'] = user.jurisdiction
					# print(request.session['user_power'])
					# print(type(request.session['user_power']))
					# 初次登录需要修改个人信息
					# 学生
					# 权限修改
					if user.have_alter == '0' and user.jurisdiction == '0':
						return redirect('/student/alter_info_stu')
					# 指导老师
					if user.have_alter == '0' and user.jurisdiction == '1':
						return redirect('/teacher/alter_info_teach')
					return redirect('/home')
				else:
					context['message'] = "您输入的密码似乎有错误!"
					return render(request, 'home/login.html', context)
			except:
				context['message'] = "您输入的账号似乎不存在！"
				return render(request, 'home/login.html', context)
		return render(request, 'home/home.html', context)
	return render(request, 'home/login.html', context)


# 注销
def logout(request):
	if not request.session.get('is_login', None):
		return redirect("/home/")
	request.session.flush()
	return redirect("/home/")


# test
def article(request):
	context = {}
	form = ArticleForm()
	context['form'] = form
	return render(request, 'test.html', context)
