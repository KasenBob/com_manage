from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import datetime
from . import models
import os
from django.db import IntegrityError
import all.models as all_model
import competition.models as competition_model
import student.models as student_model
import teacher.models as teacher_model
import news.models as news_model
from .forms import ArticleForm
from django.core.cache import cache
import xlwt
from io import BytesIO



# Create your views here.
# 增加竞赛系列
def add_series(request):
	context = {}

	if request.method == 'POST':
		series_name = request.POST.get('series_name', None)
		if series_name == None:
			context['message'] = '请输入竞赛系列名称。'
			return render(request, 'member/add_series.html', context)
		series_intro = request.POST.get('series_intro', None)
		if series_intro == None:
			context['message'] = '请输入竞赛系列简介。'
			return render(request, 'member/add_series.html', context)
		series_logo = request.FILES.get('series_logo', None)

		test = competition_model.series_info.objects.filter(name=series_name)
		if len(test) > 0:
			context['message'] = '竞赛名称重复。'
			return render(request, 'member/add_series.html', context)

		series_type = request.POST.get('series_type', None)

		series = competition_model.series_info()
		series.name = series_name
		series.introduction = series_intro
		series.type = series_type

		if series_logo != None:
			f_name = series_logo.name
			# 重命名照片
			series.photo = "series_photo/" + f_name
			url = settings.MEDIA_ROOT + 'series_photo/'
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			photo_url = open(settings.MEDIA_ROOT + "series_photo/" + f_name, 'wb')
			for chunk in series_logo.chunks():
				photo_url.write(chunk)
			photo_url.close()

		series.save()

		key = 'series_list'
		if cache.has_key(key):
			cache.delete(key)
		series_list = competition_model.series_info.objects.filter(status='0')
		cache.set(key, series_list, 30 * 60)

		return redirect('/member/my_series/')
	return render(request, 'member/add_series.html', context)


# 竞赛系列
def my_series(request):
	context = {}
	series_list = competition_model.series_info.objects.all().order_by('name')
	context['series_list'] = series_list
	for series in series_list:
		series.update_com_id()

	paginator = Paginator(series_list, 8)  # 每?篇进行分页
	page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
	page_of_series = paginator.get_page(page_num)
	current_page_num = page_of_series.number  # 获取当前页码
	# 获取当前前后各两页的页码范围
	page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
	             list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
	# 加上省略页面标记
	if page_range[0] - 1 >= 2:
		page_range.insert(0, '...')
	if paginator.num_pages - page_range[-1] >= 2:
		page_range.append('...')
	# 加上首页和尾页
	if page_range[0] != 1:
		page_range.insert(0, 1)
	if page_range[-1] != paginator.num_pages:
		page_range.append(paginator.num_pages)

	context['page_of_series'] = page_of_series
	context['page_range'] = page_range

	return render(request, 'member/my_series.html', context)


# 修改竞赛系列信息
def change_series(request):
	context = {}
	series_id = request.GET.get('p')
	series = get_object_or_404(competition_model.series_info, id=series_id)
	context['series'] = series

	if request.method == 'POST':
		series_name = request.POST.get('series_name', None)
		if series_name == None:
			context['message'] = '请输入竞赛系列名称。'
			return render(request, 'member/add_series.html', context)
		series_intro = request.POST.get('series_intro', None)
		if series_intro == None:
			context['message'] = '请输入竞赛系列简介。'
			return render(request, 'member/add_series.html', context)
		series_logo = request.FILES.get('series_logo', None)

		series_type = request.POST.get('series_type', None)

		series.name = series_name
		series.introduction = series_intro
		series.type = series_type

		if series_logo != None:
			f_name = series_logo.name
			# 重命名照片
			series.photo = "series_photo/" + f_name
			url = settings.MEDIA_ROOT + 'series_photo/'
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			photo_url = open(settings.MEDIA_ROOT + "series_photo/" + f_name, 'wb')
			for chunk in series_logo.chunks():
				photo_url.write(chunk)
			photo_url.close()

		series.save()

		key = 'series_list'
		if cache.has_key(key):
			cache.delete(key)
		series_list = competition_model.series_info.objects.filter(status='0')
		for series in series_list:
			series.update_com_id()
		cache.set(key, series_list, 30 * 60)

		return redirect('/member/my_series/')

	return render(request, 'member/change_series.html', context)


# 进行中的比赛
def my_com_ing(request):
	context = {}
	com_list = competition_model.com_basic_info.objects.exclude(com_status='3')
	context['com_list'] = com_list
	return render(request, 'member/my_com_ing.html', context)


# 历届比赛
def my_com_ed(request):
	context = {}
	com_list = competition_model.com_basic_info.objects.filter(com_status='3')
	context['com_list'] = com_list
	return render(request, 'member/my_com_ed.html', context)


# 比赛详情-参赛名单
def com_apply_detail(request):
	context = {}
	com_id = request.GET.get('p')
	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	need_info = get_object_or_404(competition_model.com_need_info, com_id=com_id)

	com_group_list = competition_model.com_group_basic_info.objects.filter(com_id=com_info)
	com_stu_list = student_model.com_stu_info.objects.filter(group_id=com_group_list)
	com_teach_list = teacher_model.com_teach_info.objects.filter(group_id=com_group_list)

	if com_info.type == '0':
		com_group_list = competition_model.com_group_basic_info.objects.filter(com_id=com_info)
		com_apply_list = []
		stu_list = []
		teach_list = []
		for com_group in com_group_list:
			com_stu = student_model.com_stu_info.objects.get(group_id=com_group)
			stu_list.append(com_stu)
			com_teach = teacher_model.com_teach_info.objects.get(group_id=com_group)
			teach_list.append(com_teach)

		com_apply_list = zip(com_group_list, stu_list, teach_list)

	context['com_info'] = com_info
	context['need_info'] = need_info
	context['com_apply_list'] = com_apply_list
	return render(request, 'member/com_apply_detail.html', context)


def com_manage(request):
	context = {}
	com_list = competition_model.com_basic_info.objects.filter()

	context['com_list'] = com_list
	return render(request, 'member/com_management.html', context)


# 学科委员-比赛详情
def com_detail_manage(request):
	context = {}
	com_id = request.GET.get('p')
	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	com_need = get_object_or_404(competition_model.com_need_info, com_id=com_id)
	com_publish = get_object_or_404(competition_model.com_publish_info, com_id=com_id)
	if com_info.com_sort_num != 0:
		sort_info = competition_model.com_sort_info.objects.filter(com_id=com_info)
		sort_list = ''
		l = len(sort_info)
		t = 1
		for sort in sort_info:
			sort_name = sort.sort_name
			if t < l:
				sort_list += (sort_name + '/')
			else:
				sort_list += (sort_name)
			t += 1
		context['sort_list'] = sort_list
	context['com_info'] = com_info
	context['com_need'] = com_need
	context['com_publish'] = com_publish
	return render(request, 'member/com_detail.html', context)


# 学科委员-比赛编辑
def com_edit(request):
	context = {}
	if request.method == 'GET':
		com_id = request.GET.get('p')
		com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
		com_need = get_object_or_404(competition_model.com_need_info, com_id=com_id)
		com_publish = get_object_or_404(competition_model.com_publish_info, com_id=com_id)
		if com_info.com_sort_num != 0:
			sort_info = competition_model.com_sort_info.objects.filter(com_id=com_info)
			sort_list = ''
			l = len(sort_info)
			t = 1
			for sort in sort_info:
				sort_name = sort.sort_name
				if t < l:
					sort_list += (sort_name + '/')
				else:
					sort_list += (sort_name)
				t += 1
			context['sort_list'] = sort_list
		context['com_info'] = com_info
		context['com_need'] = com_need
		context['com_publish'] = com_publish
		return render(request, 'member/com_edit.html', context)
	if request.method == "POST":
		com_id = request.GET.get('p')
		# 竞赛信息
		name = request.POST.get('com_name')
		begin_regit = request.POST.get('begin_regit', None)
		# begin_regit = datetime.strptime(begin_regit, "%Y-%m-%d %H:%M:%S")
		end_regit = request.POST.get('end_regit', None)
		# end_regit = datetime.strptime(end_regit, "%Y-%m-%d %H:%M:%S")
		begin_time = request.POST.get('begin_time', None)
		# begin_time = datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
		end_time = request.POST.get('end_time', None)
		# end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
		if_com_sort = request.POST.get('if_com_sort', '0')
		sort_list = request.POST.get('sort_list', '0')
		com_web = request.POST.get('com_web', '0')
		num_teach = request.POST.get('num_teach', '0')
		num_stu = request.POST.get('num_stu', '0')
		need_full = request.POST.get('need_full', '0')
		same_stu = request.POST.get('same_stu', '0')

		# 学生信息
		stu_num = request.POST.get('stu_num', '0')
		stu_name = request.POST.get('stu_name', '0')
		ID_number = request.POST.get('ID_number', '0')
		sex = request.POST.get('sex', '0')
		depart = request.POST.get('depart', '0')
		major = request.POST.get('major', '0')
		grade = request.POST.get('grade', '0')
		stu_class = request.POST.get('stu_class', '0')
		email = request.POST.get('email', '0')
		phone_num = request.POST.get('phone_num', '0')
		bank_number = request.POST.get('bank_number', '0')
		else_info = request.POST.get('else_info', '0')

		# 竞赛小组信息
		group_name = request.POST.get('group_name', '0')
		product_name = request.POST.get('product_name', '0')

		# 附件
		com_attach = request.FILES.get("com_attach", None)

		# 报名步骤
		step = request.POST.get('step', None)

		# 竞赛基本信息
		com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
		com_info.com_name = name
		com_info.begin_regit = begin_regit

		com_info.end_regit = end_regit
		com_info.begin_time = begin_time
		com_info.end_time = end_time
		com_info.num_stu = num_stu
		if need_full == '1':
			com_info.need_full = 1
		else:
			com_info.need_full = 0
		if same_stu == '1':
			com_info.same_stu = 1
		else:
			com_info.same_stu = 0
		if sort_list != '0':
			list = sort_list.split("/")
			com_info.com_sort_num = len(list)
		if com_web != '0':
			com_info.if_web = 1
			com_info.com_web = com_web
		com_info.num_teach = num_teach
		com_info.save()

		# 组别信息
		if if_com_sort == '1' and sort_list != '0':
			temp_sort = competition_model.com_sort_info.objects.filter(com_id=com_info)
			for temp in temp_sort:
				temp.delete()
			list = sort_list.split("/")
			for sort in list:
				sort_info = competition_model.com_sort_info.objects.create(com_id=com_info, sort_name=sort)

		com_need = get_object_or_404(competition_model.com_need_info, com_id=com_id)
		com_need.stu_num = stu_num
		com_need.stu_name = stu_name
		com_need.ID_number = ID_number
		com_need.sex = sex
		com_need.depart = depart
		com_need.major = major
		com_need.grade = grade
		com_need.stu_class = stu_class
		com_need.email = email
		com_need.phone_num = phone_num
		if sort_list != '0':
			com_need.com_group = 1
		else:
			com_need.com_group = 0
		com_need.group_name = group_name
		com_need.product_name = product_name
		com_need.tea_num = num_teach
		com_need.bank_number = bank_number
		com_need.else_info = else_info
		com_need.save()

		# 还差公告
		com_publish = get_object_or_404(competition_model.com_publish_info, com_id=com_info)
		if com_attach != None:
			# 取出格式名
			f_name = com_attach.name
			f_name = f_name.split('.')[-1].lower()
			# 重命名文件
			com_publish.com_attachment = "com_attach/" + str(com_info.com_id) + "/" + str(
				com_info.com_id) + "." + f_name
			url = settings.MEDIA_ROOT + 'com_attach/' + str(com_info.com_id)
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			file_url = open(settings.MEDIA_ROOT + "com_attach/" + str(com_info.com_id) + "/" + str(
				com_info.com_id) + "." + f_name,
			                'wb')
			for chunk in com_attach.chunks():
				file_url.write(chunk)
			file_url.close()
		if step != None or step != "":
			com_publish.apply_step = step
		com_publish.save()

		return redirect('/member/com_manage/')


# 学科委员—发布竞赛
def add_com(request):
	context = {}
	series_list = competition_model.series_info.objects.filter(status='0').order_by('name')
	context['series_list'] = series_list

	if request.method == "POST":
		# 竞赛信息
		series_id = request.POST.get('com_name', None)
		com_number = request.POST.get('com_number', None)

		series = get_object_or_404(competition_model.series_info, id=series_id)
		com_name = '第' + str(com_number) + '届' + series.name

		object_flag = 0
		try:
			test = competition_model.com_basic_info.objects.get(com_name=com_name)
		except ObjectDoesNotExist:
			object_flag = 1

		if object_flag != 1:
			context['message'] = "比赛已存在"
			return render(request, 'member/add_com/first.html', context)

		begin_regit = request.POST.get('begin_regit', None)

		end_regit = request.POST.get('end_regit', None)

		begin_time = request.POST.get('begin_time', None)

		end_time = request.POST.get('end_time', None)

		if_com_sort = request.POST.get('if_com_sort')

		sort_list = ''
		if if_com_sort == '1':
			sort_list = request.POST.get('sort_list')

		if_if_web = request.POST.get('if_if_web')
		if if_if_web:
			com_web = ""
			com_web = request.POST.get('com_web')

		num_teach = request.POST.get('num_teach', '0')

		num_stu = request.POST.get('num_stu', '0')

		need_full = request.POST.get('need_full', '0')

		same_stu = request.POST.get('same_stu', '0')

		# 欠缺处理
		if com_number == "":
			context['message'] = "竞赛名称要填写!"
			return render(request, 'member/add_com/first.html', context)
		if begin_regit == "":
			context['message'] = "报名开始日期要填写!"
			return render(request, 'member/add_com/first.html', context)
		if end_regit == "":
			context['message'] = "报名结束日期要填写!"
			return render(request, 'member/add_com/first.html', context)
		if begin_time == "":
			context['message'] = "比赛开始日期要填写!"
			return render(request, 'member/add_com/first.html', context)
		if num_teach == "":
			context['message'] = "指导教师人数要填写!"
			return render(request, 'member/add_com/first.html', context)
		if num_stu == "":
			context['message'] = "参赛学生人数要填写!"
			return render(request, 'member/add_com/first.html', context)

		# 学生信息
		stu_num = request.POST.get('stu_num', '0')

		stu_name = request.POST.get('stu_name', '0')

		ID_number = request.POST.get('ID_number', '0')

		sex = request.POST.get('sex', '0')

		depart = request.POST.get('depart', '0')

		major = request.POST.get('major', '0')

		grade = request.POST.get('grade', '0')

		stu_class = request.POST.get('stu_class', '0')

		email = request.POST.get('email', '0')

		phone_num = request.POST.get('phone_num', '0')

		bank_number = request.POST.get('bank_number', '0')

		else_info = request.POST.get('else_info', '0')

		# 竞赛小组信息
		group_name = request.POST.get('group_name', '0')

		product_name = request.POST.get('product_name', '0')

		# 输入数据库
		com_info = competition_model.com_basic_info()
		com_info.com_name = com_name
		com_info.series_id = series
		if int(num_stu) > 1:
			com_info.type = 1
		else:
			com_info.type = 0
		com_info.begin_regit = begin_regit
		com_info.end_regit = end_regit
		com_info.begin_time = begin_time
		com_info.end_time = end_time
		com_info.num_stu = num_stu
		if need_full == '1':
			com_info.need_full = 1
		else:
			com_info.need_full = 0
		if same_stu == '1':
			com_info.same_stu = 1
		else:
			com_info.same_stu = 0
		if if_com_sort != '0':
			list = sort_list.split("/")
			com_info.com_sort_num = len(list)
		if if_if_web != '0':
			com_info.if_web = 1
			com_info.com_web = com_web
		com_info.num_teach = num_teach
		com_info.com_status = '0'
		com_info.save()

		if sort_list != '0':
			list = sort_list.split("/")
			for sort in list:
				sort_info = competition_model.com_sort_info.objects.create(com_id=com_info, sort_name=sort)

		com_need = competition_model.com_need_info()
		com_need.com_id = com_info.com_id
		com_need.stu_num = int(stu_num)
		com_need.stu_name = int(stu_name)
		com_need.ID_number = int(ID_number)
		com_need.sex = int(sex)
		com_need.depart = int(depart)
		com_need.major = int(major)
		com_need.grade = int(grade)
		com_need.stu_class = int(stu_class)
		com_need.email = int(email)
		com_need.phone_num = int(phone_num)
		if sort_list != '0':
			com_need.com_group = int(1)
		else:
			com_need.com_group = int(0)
		com_need.group_name = int(group_name)
		com_need.product_name = int(product_name)
		com_need.tea_num = int(num_teach)
		com_need.bank_number = int(bank_number)
		com_need.else_info = int(else_info)
		com_need.save()

		key = 'com_list'
		if cache.has_key(key):
			cache.delete(key)
		com_list = competition_model.com_basic_info.objects.filter(com_status='0')
		cache.set(key, com_list, 30 * 60)

		return redirect('/member/add_notices/')

	return render(request, 'member/add_com/first.html', context)


# 学科委员—增加公告
@csrf_exempt
def add_notices(request):
	context = {}
	form = ArticleForm()
	context['form'] = form

	com_list = competition_model.com_basic_info.objects.exclude(com_status='3').order_by('-begin_regit')
	context['com_list'] = com_list

	if request.method == "POST":
		com_id = request.POST.get('com_id', None)
		if com_id != None and com_id != '无':
			com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
		com_attach = request.FILES.get('com_attach', None)
		author = request.POST.get('author', None)

		title = request.POST.get('title', '公告')

		test_list = all_model.inform.objects.filter(title=title)
		if len(test_list) > 0:
			context['message'] = "已存在同标题公告，请更改标题！"
			return render(request, 'member/add_com/second.html', context)

		apply_form = ArticleForm(request.POST)
		content = ''
		if apply_form.is_valid():
			content = apply_form.cleaned_data['content']

		inform = all_model.inform()
		if com_id != None and com_id != '无':
			inform.com_id = com_info
		else:
			inform.com_id = None
		inform.title = title
		inform.content = content
		inform.author = author
		if com_attach != None:
			# 取出格式名
			f_name = com_attach.name
			f_name = f_name.split('.')[-1].lower()
			# 重命名文件
			inform.com_attachment = "com_attach\\" + str(title) + "\\." + str(title) + '.' + f_name
			# print(com_publish.com_attachment)
			url = settings.MEDIA_ROOT + 'com_attach\\' + str(title)
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			file_url = open(settings.MEDIA_ROOT + "com_attach\\" + str(title) + "\\." + str(title) + '.' + f_name, 'wb')
			for chunk in com_attach.chunks():
				file_url.write(chunk)
			file_url.close()
		inform.save()
		return redirect('/member/notice_comanage/')
	return render(request, 'member/add_com/second.html', context)


# 修改小组信息申请
def apply_application(request):
	context = {}
	temp_group_list = competition_model.temp_com_group_basic_info.objects.all()
	pre_stu_list = []
	temp_com_stu_list = []
	pre_teach_list = []
	temp_com_teach_list = []
	com_need_list = []
	for temp_group in temp_group_list:
		pre_stu = student_model.com_stu_info.objects.filter(group_id=temp_group.group_id)
		pre_stu_list.append(pre_stu)
		stu_list = student_model.temp_com_stu_info.objects.filter(temp_id=temp_group)
		temp_com_stu_list.append(stu_list)
		pre_teach = teacher_model.com_teach_info.objects.filter(group_id=temp_group.group_id)
		pre_teach_list.append(pre_teach)
		teach_list = teacher_model.temp_com_teach_info.objects.filter(temp_id=temp_group)
		temp_com_teach_list.append(teach_list)
		com_need = get_object_or_404(competition_model.com_need_info, com_id=temp_group.com_id.com_id)
		com_need_list.append(com_need)

	temp_group_list = zip(temp_group_list, temp_com_stu_list, pre_stu_list, temp_com_teach_list, pre_teach_list,
	                      com_need_list)
	context['temp_group_list'] = temp_group_list
	return render(request, 'member/group_change.html', context)


# 同意小组信息修改
def apply_application_agree(request):
	temp_id = request.GET.get('p')
	temp_info = get_object_or_404(competition_model.temp_com_group_basic_info, temp_id=temp_id)
	group_info = temp_info.group_id

	if temp_info.apply_type == '1':
		# 修改小组信息
		group_info.group_name = temp_info.group_name
		group_info.group_num = temp_info.group_num
		group_info.com_group = temp_info.com_group
		group_info.product_name = temp_info.product_name
		group_info.else_info = temp_info.else_info
		group_info.save()

		# 修改小组学生信息
		temp_stu_list = student_model.temp_com_stu_info.objects.filter(temp_id=temp_info)
		pre_stu_list = student_model.com_stu_info.objects.filter(group_id=group_info)
		for pre_stu in pre_stu_list:
			pre_stu.delete()
		for temp_stu in temp_stu_list:
			new_stu = student_model.com_stu_info()
			new_stu.com_id = group_info.com_id
			new_stu.group_id = group_info
			new_stu.stu_id = temp_stu.stu_id
			new_stu.is_leader = temp_stu.is_leader
			new_stu.status = '1'
			new_stu.save()
			temp_stu.delete()

		# 修改指导教师信息
		temp_teach_list = teacher_model.temp_com_teach_info.objects.filter(temp_id=temp_info)
		pre_teach_list = teacher_model.com_teach_info.objects.filter(group_id=group_info)
		for pre_teach in pre_teach_list:
			pre_teach.delete()
		for temp_teach in temp_teach_list:
			new_teach = teacher_model.com_teach_info()
			new_teach.com_id = group_info.com_id
			new_teach.group_id = group_info
			new_teach.teach_id = temp_teach.teach_id
			new_teach.status = '1'
			new_teach.save()
			temp_teach.delete()

		temp_info.delete()
	else:
		temp_stu_list = student_model.temp_com_stu_info.objects.filter(temp_id=temp_info)
		pre_stu_list = student_model.com_stu_info.objects.filter(group_id=group_info)
		for pre_stu in pre_stu_list:
			pre_stu.delete()
		for temp_stu in temp_stu_list:
			temp_stu.delete()

		temp_teach_list = teacher_model.temp_com_teach_info.objects.filter(temp_id=temp_info)
		pre_teach_list = teacher_model.com_teach_info.objects.filter(group_id=group_info)
		for pre_teach in pre_teach_list:
			pre_teach.delete()
		for temp_teach in temp_teach_list:
			temp_teach.delete()

		# 要发信息

		temp_info.delete()
		group_info.delete()

	return redirect('/member/apply_application/')


# 驳回小组信息修改
def apply_application_disagree(request):
	temp_id = request.GET.get('p')
	temp_info = get_object_or_404(competition_model.temp_com_group_basic_info, temp_id=temp_id)

	temp_stu_list = student_model.temp_com_stu_info.objects.filter(temp_id=temp_info)
	for temp_stu in temp_stu_list:
		temp_stu.delete()
	temp_teach_list = teacher_model.temp_com_teach_info.objects.filter(temp_id=temp_info)
	for temp_teach in temp_teach_list:
		temp_teach.delete()

	return redirect('/member/apply_application/')


# 个人信息修改申请
def msg_application(request):
	context = {}
	msg_stu_list = student_model.temp_stu_basic_info.objects.all()
	# get pre
	pre_stu_list = []
	for stu in msg_stu_list:
		pre_stu = student_model.stu_basic_info.objects.get(stu_number=stu.stu_number.stu_number)
		pre_stu_list.append(pre_stu)
	msg_stu_list = zip(pre_stu_list, msg_stu_list)
	context['msg_stu_list'] = msg_stu_list

	msg_teach_list = teacher_model.temp_teach_basic_info.objects.all()
	# get pre
	pre_teach_list = []
	for teach in msg_teach_list:
		pre_teach = teacher_model.teach_basic_info.objects.get(tea_number=teach.teach_number.tea_number)
		pre_teach_list.append(teach)
	msg_teach_list = zip(pre_teach_list, msg_teach_list)
	context['msg_teach_list'] = msg_teach_list

	return render(request, 'member/audit_change.html', context)


# 通过个人信息修改申请
def msg_application_agree(request):
	context = {}
	# type_id=0:学生；type_id=1:指导教师
	type_id = request.GET.get('p1')
	temp_id = request.GET.get('p2')
	if type_id == '0':
		temp_stu = get_object_or_404(student_model.temp_stu_basic_info, pk=temp_id)
		pre_stu = temp_stu.stu_number
		pre_stu.stu_name = temp_stu.stu_name
		pre_stu.department = temp_stu.department
		pre_stu.major = temp_stu.major
		pre_stu.grade = temp_stu.grade
		pre_stu.stu_class = temp_stu.stu_class
		pre_stu.sex = temp_stu.sex
		pre_stu.ID_number = temp_stu.ID_number
		pre_stu.save()
		temp_stu.delete()
	else:
		temp_teach = get_object_or_404(teacher_model.temp_teach_basic_info, pk=temp_id)
		pre_teach = temp_teach.teach_number
		pre_teach.tea_name = temp_teach.tea_name
		pre_teach.profess = temp_teach.profess
		pre_teach.department = temp_teach.department
		pre_teach.save()
		temp_teach.delete()
	return redirect('/member/msg_application/')


# 驳回个人信息修改申请
def msg_application_disagree(request):
	# type_id=0:学生；type_id=1:指导教师
	type_id = request.GET.get('p1')
	temp_id = request.GET.get('p2')
	if type_id == '0':
		temp_stu = get_object_or_404(student_model.temp_stu_basic_info, pk=temp_id)
		temp_stu.delete()
	else:
		temp_teach = get_object_or_404(teacher_model.temp_teach_basic_info, pk=temp_id)
		temp_teach.delete()
	return redirect('/member/msg_application/')


# 新闻管理
def release_manage(request):
	context = {}
	news_list = news_model.news.objects.all()
	context['news_list'] = news_list
	return render(request, 'member/release_manage.html', context)


# 发布新闻
def add_news(request):
	context = {}
	form = ArticleForm()
	context['form'] = form

	if request.method == "POST":
		title = request.POST.get('title')
		apply_form = ArticleForm(request.POST)
		content = ''
		if apply_form.is_valid():
			content = apply_form.cleaned_data['content']
		author = request.POST.get('author')
		photo = request.FILES.get('photo')

		news = news_model.news()
		news.title = title
		news.content = content
		news.author = author

		if photo != None:
			f_name = photo.name
			news.new_photo = "news/" + f_name
			url = settings.MEDIA_ROOT + 'news'
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			photo_url = open(settings.MEDIA_ROOT + "news/" + f_name, 'wb')
			for chunk in photo.chunks():
				photo_url.write(chunk)
			photo_url.close()
		news.save()
		return redirect('/member/news_comanage/')

	return render(request, 'member/add_com/add_news.html', context)


# 新闻管理
def news_comanage(request):
	context = {}

	news_list = news_model.news.objects.all().order_by('-last_update_time')

	paginator = Paginator(news_list, 12)  # 每?篇进行分页
	page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
	page_of_news = paginator.get_page(page_num)
	current_page_num = page_of_news.number  # 获取当前页码
	# 获取当前前后各两页的页码范围
	page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
	             list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
	# 加上省略页面标记
	if page_range[0] - 1 >= 2:
		page_range.insert(0, '...')
	if paginator.num_pages - page_range[-1] >= 2:
		page_range.append('...')
	# 加上首页和尾页
	if page_range[0] != 1:
		page_range.insert(0, 1)
	if page_range[-1] != paginator.num_pages:
		page_range.append(paginator.num_pages)

	context['page_of_news'] = page_of_news
	context['page_range'] = page_range

	return render(request, 'member/news_manage.html', context)


# 修改新闻
def change_news(request):
	context = {}

	news_id = request.GET.get('p')
	# print(news_id)
	news = get_object_or_404(news_model.news, pk=news_id)
	# print(new)
	if request.method == 'POST':

		title = request.POST.get('title')
		apply_form = ArticleForm(request.POST)
		content = ''
		if apply_form.is_valid():
			content = apply_form.cleaned_data['content']
		author = request.POST.get('author')
		photo = request.FILES.get('photo')

		news.title = title
		news.content = content
		news.author = author

		if photo != None:
			f_name = photo.name
			news.new_photo = "news/" + f_name
			url = settings.MEDIA_ROOT + 'news'
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			photo_url = open(settings.MEDIA_ROOT + "news/" + f_name, 'wb')
			for chunk in photo.chunks():
				photo_url.write(chunk)
			photo_url.close()
		news.save()
		return redirect('/member/news_comanage/')

	ini = {'content': news.content}
	form = ArticleForm(initial=ini)
	context['new'] = news
	context['form'] = form
	return render(request, 'member/change_news.html', context)


# 删除新闻
def delete_news(request):
	context = {}
	new_id = request.GET.get('p')
	new = get_object_or_404(news_model.news, pk=new_id)
	new.delete()
	return redirect('/member/news_comanage/')


# 公告管理
def notice_comanage(request):
	context = {}

	inform_list = all_model.inform.objects.all().order_by('-create_time')

	paginator = Paginator(inform_list, 12)  # 每?篇进行分页
	page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
	page_of_inform = paginator.get_page(page_num)
	current_page_num = page_of_inform.number  # 获取当前页码
	# 获取当前前后各两页的页码范围
	page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
	             list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
	# 加上省略页面标记
	if page_range[0] - 1 >= 2:
		page_range.insert(0, '...')
	if paginator.num_pages - page_range[-1] >= 2:
		page_range.append('...')
	# 加上首页和尾页
	if page_range[0] != 1:
		page_range.insert(0, 1)
	if page_range[-1] != paginator.num_pages:
		page_range.append(paginator.num_pages)

	context['page_of_inform'] = page_of_inform
	context['page_range'] = page_range

	return render(request, 'member/notice_comanage.html', context)


# 修改公告
def change_notice(request):
	context = {}

	com_list = competition_model.com_basic_info.objects.exclude(com_status='3').order_by('-begin_regit')
	context['com_list'] = com_list

	notice_id = request.GET.get('p')
	# print(news_id)
	notice = get_object_or_404(all_model.inform, pk=notice_id)
	# print(new)
	if request.method == 'POST':

		title = request.POST.get('title')
		apply_form = ArticleForm(request.POST)
		content = ''
		if apply_form.is_valid():
			content = apply_form.cleaned_data['content']
		author = request.POST.get('author')
		photo = request.FILES.get('photo')
		com_id = request.POST.get('com_id', None)
		if com_id != None and com_id != '无':
			com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
		if com_id != None and com_id != '无':
			notice.com_id = com_info

		notice.title = title
		notice.content = content
		notice.author = author

		notice.save()
		return redirect('/member/notice_comanage/')

	ini = {'content': notice.content}
	form = ArticleForm(initial=ini)
	context['notice'] = notice
	context['form'] = form
	return render(request, 'member/change_notice.html', context)


# 删除公告
def delete_notice(request):
	context = {}
	notice_id = request.GET.get('p')
	# print(news_id)
	notice = get_object_or_404(all_model.inform, pk=notice_id)
	notice.delete()
	return redirect('/member/notice_comanage/')


# 比赛管理
def my_coms(request):
	context = {}
	com_list = competition_model.com_basic_info.objects.all().order_by('-begin_regit')
	context['com_list'] = com_list
	for com in com_list:
		com.update_status()

	paginator = Paginator(com_list, 8)  # 每?篇进行分页
	page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
	page_of_coms = paginator.get_page(page_num)
	current_page_num = page_of_coms.number  # 获取当前页码
	# 获取当前前后各两页的页码范围
	page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
	             list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
	# 加上省略页面标记
	if page_range[0] - 1 >= 2:
		page_range.insert(0, '...')
	if paginator.num_pages - page_range[-1] >= 2:
		page_range.append('...')
	# 加上首页和尾页
	if page_range[0] != 1:
		page_range.insert(0, 1)
	if page_range[-1] != paginator.num_pages:
		page_range.append(paginator.num_pages)

	context['page_of_coms'] = page_of_coms
	context['page_range'] = page_range

	return render(request, 'member/my_coms.html', context)


# 切换比赛系列状态
def change_series_status(request):
	context = {}
	series_id = request.GET.get('p')
	series = get_object_or_404(competition_model.series_info, id=series_id)
	if series.status == '0':
		series.status = '1'
	else:
		series.status = '0'
	series.save()
	# 删除缓存
	key = 'series_list'
	if cache.has_key(key):
		cache.delete(key)
	series_list = competition_model.series_info.objects.filter(status='0')
	cache.set(key, series_list, 30 * 60)
	return redirect('/member/my_series/')


# 修改比赛
def change_com(request):
	context = {}
	com_id = request.GET.get("p")
	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	com_need = get_object_or_404(competition_model.com_need_info, com_id=com_id)
	series_list = competition_model.series_info.objects.all().order_by('name')
	context['series_list'] = series_list
	begin = com_info.com_name.find("第")
	end = com_info.com_name.find("届")
	jieshu = ""
	for i in range(begin + 1, end):
		jieshu += com_info.com_name[i]
	#print(jieshu)
	begin_regit = str(com_info.begin_regit).replace(' ', 'T')
	context['begin_regit'] = begin_regit
	end_regit = str(com_info.end_regit).replace(' ', 'T')
	context['end_regit'] = end_regit
	begin_time = str(com_info.begin_time).replace(' ', 'T')
	context['begin_time'] = begin_time
	end_time = str(com_info.end_time).replace(' ', 'T')
	context['end_time'] = end_time
	if com_info.com_sort_num != 0:
		sort_info = competition_model.com_sort_info.objects.filter(com_id=com_info)
		sort_list = ''
		l = len(sort_info)
		t = 1
		for sort in sort_info:
			sort_name = sort.sort_name
			if t < l:
				sort_list += (sort_name + '/')
			else:
				sort_list += (sort_name)
			t += 1
		context['sort_list'] = sort_list
	context['com_info'] = com_info
	context['com_need'] = com_need
	context['jieshu'] = jieshu
	if request.method == 'POST':
		series_id = request.POST.get('com_name', None)
		com_number = request.POST.get('com_number', None)

		series = get_object_or_404(competition_model.series_info, id=series_id)
		com_name = '第' + str(com_number) + '届' + series.name
		object_flag = 0
		try:
			test_com = competition_model.com_basic_info.objects.get(com_name=com_name)
		except ObjectDoesNotExist:
			object_flag = 1
		if object_flag != 1:
			if com_name != test_com.com_name:
				context['message'] = "比赛已存在"
				return render(request, 'member/change_com.html', context)
		begin_regit = request.POST.get('begin_regit', None)
		end_regit = request.POST.get('end_regit', None)
		begin_time = request.POST.get('begin_time', None)
		end_time = request.POST.get('end_time', None)
		if_com_sort = request.POST.get('if_com_sort')
		sort_list = ''
		if if_com_sort == '1':
			sort_list = request.POST.get('sort_list')
		if_if_web = request.POST.get('if_if_web')
		if if_if_web:
			com_web = request.POST.get('com_web')
		num_teach = request.POST.get('num_teach', '0')
		num_stu = request.POST.get('num_stu', '0')
		need_full = request.POST.get('need_full', '0')
		same_stu = request.POST.get('same_stu', '0')
		# 欠缺处理
		if com_number == "":
			context['message'] = "竞赛名称要填写!"
			return render(request, 'member/change_com.html', context)
		if begin_regit == "":
			context['message'] = "报名开始日期要填写!"
			return render(request, 'member/change_com.html', context)
		if end_regit == "":
			context['message'] = "报名结束日期要填写!"
			return render(request, 'member/change_com.html', context)
		if begin_time == "":
			context['message'] = "比赛开始日期要填写!"
			return render(request, 'member/change_com.html', context)
		if num_teach == "":
			context['message'] = "指导教师人数要填写!"
			return render(request, 'member/change_com.html', context)
		if num_stu == "":
			context['message'] = "参赛学生人数要填写!"
			return render(request, 'member/change_com.html', context)
		# 学生信息
		stu_num = request.POST.get('stu_num', '0')
		stu_name = request.POST.get('stu_name', '0')
		ID_number = request.POST.get('ID_number', '0')
		sex = request.POST.get('sex', '0')
		depart = request.POST.get('depart', '0')
		major = request.POST.get('major', '0')
		grade = request.POST.get('grade', '0')
		stu_class = request.POST.get('stu_class', '0')
		email = request.POST.get('email', '0')
		phone_num = request.POST.get('phone_num', '0')
		bank_number = request.POST.get('bank_number', '0')
		else_info = request.POST.get('else_info', '0')
		# 竞赛小组信息
		group_name = request.POST.get('group_name', '0')
		product_name = request.POST.get('product_name', '0')
		# 修改数据库
		com_info.com_name = com_name
		com_info.series_id = series
		if int(num_stu) > 1:
			com_info.type = 1
		else:
			com_info.type = 0
		com_info.begin_regit = begin_regit
		com_info.end_regit = end_regit
		com_info.begin_time = begin_time
		com_info.end_time = end_time
		com_info.num_stu = num_stu
		if need_full == '1':
			com_info.need_full = 1
		else:
			com_info.need_full = 0
		if same_stu == '1':
			com_info.same_stu = 1
		else:
			com_info.same_stu = 0
		if if_com_sort != '0':
			list = sort_list.split("/")
			com_info.com_sort_num = len(list)
		if if_if_web != '0':
			com_info.if_web = 1
			com_info.com_web = com_web
		com_info.num_teach = num_teach
		com_info.com_status = '0'
		com_info.save()
		com_info.update_status

		if if_com_sort == '1' and sort_list != '0':
			temp_sort = competition_model.com_sort_info.objects.filter(com_id=com_info)
			for temp in temp_sort:
				temp.delete()
			list = sort_list.split("/")
			for sort in list:
				sort_info = competition_model.com_sort_info.objects.create(com_id=com_info, sort_name=sort)

		com_need.com_id = com_info.com_id
		com_need.stu_num = int(stu_num)
		com_need.stu_name = int(stu_name)
		com_need.ID_number = int(ID_number)
		com_need.sex = int(sex)
		com_need.depart = int(depart)
		com_need.major = int(major)
		com_need.grade = int(grade)
		com_need.stu_class = int(stu_class)
		com_need.email = int(email)
		com_need.phone_num = int(phone_num)
		if sort_list != '0':
			com_need.com_group = int(1)
		else:
			com_need.com_group = int(0)
		com_need.group_name = int(group_name)
		com_need.product_name = int(product_name)
		com_need.tea_num = int(num_teach)
		com_need.bank_number = int(bank_number)
		com_need.else_info = int(else_info)
		com_need.save()

		key = 'com_list'
		if cache.has_key(key):
			cache.delete(key)
		com_list = competition_model.com_basic_info.objects.filter(com_status='0')
		cache.set(key, com_list, 30 * 60)

		return redirect('/member/my_coms/')
	return render(request, 'member/change_com.html', context)


# 修改密码
def edit_pwd(request):
	context = {}

	if request.method == 'POST':
		user_info = get_object_or_404(all_model.user_login_info, account=request.session['user_number'])
		pre_pwd = request.POST.get('pre_pwd')
		new_pwd = request.POST.get('new_pwd_2')

		if user_info.psword != pre_pwd:
			context['message'] = "原密码不正确!"
			return render(request, 'member/edit_pwd.html', context)

		user_info.psword = new_pwd
		user_info.save()
		return redirect('/member/add_com/')

	return render(request, 'member/edit_pwd.html', context)


# 导出到excel
def export_excel(request):
	com_id = request.GET.get('p')
	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	need_info = get_object_or_404(competition_model.com_need_info, com_id=com_id)

	com_group_list = competition_model.com_group_basic_info.objects.filter(com_id=com_info, status='1')
	com_stu_list = student_model.com_stu_info.objects.filter(group_id=com_group_list)
	com_teach_list = teacher_model.com_teach_info.objects.filter(group_id=com_group_list)
	if com_info.type == '0':
		# 设置HTTPResponse的类型
		response = HttpResponse(content_type='application/vnd.ms-excel')
		filename = com_info.com_name + '报名表'
		response['Content-Disposition'] = 'attachment;filename=Registration_form.xls'
		# 创建一个文件对象
		wb = xlwt.Workbook(encoding='utf8')
		# 创建一个sheet对象
		sheet = wb.add_sheet('order-sheet')

		# 写入文件标题
		data_line = 0

		sheet.write(0, data_line, '序号')
		data_line += 1

		if need_info.stu_num == 1:
			sheet.write(0, data_line, '学号')
			data_line += 1

		if need_info.stu_name == 1:
			sheet.write(0, data_line, '姓名')
			data_line += 1

		if need_info.depart == 1:
			sheet.write(0, data_line, '院系')
			data_line += 1

		if need_info.major == 1:
			sheet.write(0, data_line, '专业')
			data_line += 1

		if need_info.grade == 1:
			sheet.write(0, data_line, '年级')
			data_line += 1

		if need_info.stu_class == 1:
			sheet.write(0, data_line, '班级')
			data_line += 1

		if need_info.ID_number == 1:
			sheet.write(0, data_line, '身份证号')
			data_line += 1

		if need_info.sex == 1:
			sheet.write(0, data_line, '性别')
			data_line += 1

		if need_info.email == 1:
			sheet.write(0, data_line, '邮箱')
			data_line += 1

		if need_info.phone_num == 1:
			sheet.write(0, data_line, '联系电话')
			data_line += 1

		if need_info.bank_number == 1:
			sheet.write(0, data_line, '银行卡号')
			data_line += 1

		if need_info.tea_num != 0:
			sheet.write(0, data_line, '指导教师')
			data_line += 1

		if need_info.else_info == 1:
			sheet.write(0, data_line, '备注')
			data_line += 1

		# 整合
		stu_list = []
		teach_list = []
		for com_group in com_group_list:
			com_stu = student_model.com_stu_info.objects.get(group_id=com_group)
			stu_list.append(com_stu)
			com_teach = teacher_model.com_teach_info.objects.get(group_id=com_group)
			teach_list.append(com_teach)
		com_apply_list = zip(com_group_list, stu_list, teach_list)

		# 写入数据
		data_row = 1
		for com_group, stu, teach in com_apply_list:
			data_line = 0
			sheet.write(data_row, data_line, data_row)
			data_line += 1
			if need_info.stu_num == 1:
				sheet.write(data_row, data_line, stu.stu_id.stu_number)
				data_line += 1
			if need_info.stu_name == 1:
				sheet.write(data_row, data_line, stu.stu_id.stu_name)
				data_line += 1
			if need_info.depart == 1:
				sheet.write(data_row, data_line, stu.stu_id.department.depart_name)
				data_line += 1
			if need_info.major == 1:
				sheet.write(data_row, data_line, stu.stu_id.major.major_name)
				data_line += 1
			if need_info.grade == 1:
				sheet.write(data_row, data_line, stu.stu_id.grade.grade_name)
				data_line += 1
			if need_info.stu_class == 1:
				sheet.write(data_row, data_line, stu.stu_id.stu_class.class_name)
				data_line += 1
			if need_info.ID_number == 1:
				sheet.write(data_row, data_line, stu.stu_id.ID_number)
				data_line += 1
			if need_info.sex == 1:
				sheet.write(data_row, data_line, stu.stu_id.sex)
				data_line += 1
			if need_info.email == 1:
				sheet.write(data_row, data_line, stu.stu_id.email)
				data_line += 1
			if need_info.phone_num == 1:
				sheet.write(data_row, data_line, stu.stu_id.phone_number)
				data_line += 1
			if need_info.bank_number == 1:
				sheet.write(data_row, data_line, stu.stu_id.bank_number)
				data_line += 1
			if need_info.tea_num != 0:
				sheet.write(data_row, data_line, teach.teach_id.tea_name)
				data_line += 1
			if need_info.else_info == 1:
				sheet.write(data_row, data_line, com_group.else_info)
				data_line += 1
			data_row = data_row + 1

		# 写出到IO
		output = BytesIO()
		wb.save(output)
		# 重新定位到开始
		output.seek(0)
		response.write(output.getvalue())
		return response
