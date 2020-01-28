from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from datetime import datetime
from django.core.paginator import Paginator
from . import models
import os
import all.models as all_model
import competition.models as competition_model
import teacher.models as teacher_model
import student.models as student_model
from .tasks import send_stu_inform
from teacher.tasks import send_teach_inform


# Create your views here.
# 学生修改个人信息
def alter_info_stu(request):
	context = {}
	nid = request.session.get('user_number', None)
	user_info = get_object_or_404(all_model.user_login_info, account=nid)
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=nid)
	depart_info = all_model.depart_info.objects.all()
	major_info = all_model.major_info.objects.all()
	grade_info = all_model.grade_info.objects.all()
	class_info = all_model.class_info.objects.all()

	context = {}
	context['stu_info'] = stu_info
	context['depart_info'] = depart_info
	context['major_info'] = major_info
	context['grade_info'] = grade_info
	context['class_info'] = class_info
	context['user_info'] = user_info

	if user_info.have_alter == '0':
		context['message'] = "需确认个人信息无误后方可进行报名等操作。"

	# print(context['stu'][0])
	if request.method == "POST":
		stu_number = request.POST.get('stu_number')
		stu_number = get_object_or_404(models.stu_basic_info, stu_number=stu_number)
		stu_name = request.POST.get('stu_name').strip()
		department = request.POST.get('department')
		department = get_object_or_404(all_model.depart_info, depart_name=department)
		major = request.POST.get('major')
		major = get_object_or_404(all_model.major_info, major_name=major)
		grade = request.POST.get('grade')
		grade = get_object_or_404(all_model.grade_info, grade_name=grade)
		stu_class = request.POST.get('stu_class')
		stu_class = get_object_or_404(all_model.class_info, class_name=stu_class)
		sex = request.POST.get('sex')
		ID_number = request.POST.get('ID_number')
		reason = request.POST.get('liyou')

		if major.depart != department:
			context['message'] = "专业与院系不符！"
			return render(request, 'student/personal_center/my_info.html', context)

		if ID_number == None or ID_number == "" or ID_number == 'None':
			context['message'] = "请务必填写身份证号！"
			return render(request, 'student/personal_center/my_info.html', context)

		bank_number = request.POST.get('bank_number')
		phone_number = request.POST.get('phone_number')

		if phone_number == None or phone_number == "" or phone_number == 'None':
			context['message'] = "请务必填写手机号码！"
			return render(request, 'student/personal_center/my_info.html', context)

		email = request.POST.get('email')

		if email == None or email == "" or email == 'None':
			context['message'] = "请务必填写邮箱！"
			return render(request, 'student/personal_center/my_info.html', context)

		stu_info = models.stu_basic_info.objects.get(stu_number=nid)
		flag = 1
		if stu_info.stu_name != stu_name:
			flag = 0
		if stu_info.department != department:
			flag = 0
		if stu_info.major != major:
			flag = 0
		if stu_info.grade != grade:
			flag = 0
		if stu_info.stu_class != stu_class:
			flag = 0
		if stu_info.ID_number != ID_number:
			flag = 0
		if stu_info.sex != sex:
			flag = 0

		if flag == 0:
			temp_stu_info = models.temp_stu_basic_info()
			temp_stu_info.stu_number = stu_number
			temp_stu_info.stu_name = stu_name
			temp_stu_info.department = department
			temp_stu_info.major = major
			temp_stu_info.grade = grade
			temp_stu_info.stu_class = stu_class
			temp_stu_info.ID_number = ID_number
			temp_stu_info.sex = sex
			temp_stu_info.reason = reason
			temp_stu_info.save()
			# 发送通知
			stu_id = stu_info.stu_number
			title = '个人信息修改申请'
			content = '您已成功提交个人信息修改申请，请等待学科委员审核。'
			send_stu_inform(stu_id, title, content)

		# stu_info.stu_number = stu_number
		# stu_info.stu_name = stu_name

		# stu_info.department = get_object_or_404(all_model.depart_info, depart_name=department)
		# stu_info.major = get_object_or_404(all_model.major_info, major_name=major)
		# stu_info.grade = get_object_or_404(all_model.grade_info, grade_name=grade)
		# stu_info.stu_class = get_object_or_404(all_model.class_info, class_name=stu_class)
		# stu_info.ID_number = ID_number
		stu_info.bank_number = bank_number
		stu_info.phone_number = phone_number
		stu_info.email = email

		stu_info.save()
		# 更改修改状态

		user_login = get_object_or_404(all_model.user_login_info, account=request.session['user_number'])
		user_login.have_login = '1'
		user_login.have_alter = '1'
		user_login.save()

		return redirect('/student/personal_center_stu_info')
	# stu_info = stu_basic_Form()
	return render(request, 'student/personal_center/alter_info.html', context)


# 修改头像
def alter_avatar(request):
	context = {}
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info
	if request.method == "POST":
		photo = request.FILES.get("avatar_file")
		if photo != None:
			f_name = photo.name
			f_name = f_name.split('.')[-1].lower()
			# 重命名照片
			stu_info.photo = "stu_photo/" + stu_info.stu_number + "/" + 'head' + '.' + f_name
			url = settings.MEDIA_ROOT + 'stu_photo/' + stu_info.stu_number
			# 判断路径是否存在
			isExists = os.path.exists(url)
			if not isExists:
				os.makedirs(url)
			photo_url = open(settings.MEDIA_ROOT + "stu_photo/" + stu_info.stu_number + "/" + 'head' + '.' + f_name,
			                 'wb')
			for chunk in photo.chunks():
				photo_url.write(chunk)
			photo_url.close()
			stu_info.save()
	return render(request, 'student/personal_center/alter_avatar.html', context)


# 学生个人中心-报名
def personal_center_stu_apply(request):
	context = {}
	# 获取图片
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info
	apply_list = models.com_stu_info.objects.filter(stu_id=stu_info.stu_number).order_by('-group_id')
	apply_one_list = []
	apply_all_list = []
	leader_list = []
	change_one_list = []
	change_all_list = []
	for apply in apply_list:
		if apply.com_id.type == '0' and apply.com_id.com_status != '3':
			apply_one_list.append(apply)
			temp = competition_model.temp_com_group_basic_info.objects.filter(group_id=apply.group_id)
			flag = 0
			if len(temp) > 0:
				flag = 1
			change_one_list.append(flag)
		elif apply.com_id.type == '1' and apply.com_id.com_status != '3':
			apply_all_list.append(apply)
			group = apply.group_id
			temp = competition_model.temp_com_group_basic_info.objects.filter(group_id=apply.group_id)
			flag = 0
			if len(temp) > 0:
				flag = 1
			change_all_list.append(flag)
			stu_list = models.com_stu_info.objects.filter(group_id=group)
			for stu in stu_list:
				if stu.is_leader == 1:
					leader_list.append(stu)
	apply_one = zip(apply_one_list, change_one_list)
	apply_all = zip(apply_all_list, leader_list, change_all_list)

	context['apply_one'] = apply_one
	context['apply_all'] = apply_all
	return render(request, 'student/personal_center/my_apply.html', context)


# 学生个人中心-信息
def personal_center_stu_message(request):
	context = {}

	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info
	informs_list = models.stu_inform.objects.filter(
		Recipient_acc=get_object_or_404(all_model.user_login_info, account=request.session['user_number'])).order_by(
		'-create_time')

	inform_flag = 0
	if len(informs_list) == 0:
		inform_flag = 0
	else:
		inform_flag = 1
	context['inform_flag'] = inform_flag

	paginator = Paginator(informs_list, 4)  # 每?篇进行分页
	page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
	page_of_informs = paginator.get_page(page_num)
	current_page_num = page_of_informs.number  # 获取当前页码
	# 获取当前前后各两页的页码范围
	page_range = list(range(max(current_page_num, 1), current_page_num)) + \
	             list(range(current_page_num, min(current_page_num, paginator.num_pages) + 1))
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

	if request.GET.get('p') != None:
		inform_id = request.GET.get('p')
		context['inform'] = models.stu_inform.objects.get(pk=inform_id)
	elif inform_flag == 1:
		context['inform'] = informs_list[0]

	context['page_of_informs'] = page_of_informs
	context['page_range'] = page_range
	context['informs'] = informs_list
	return render(request, 'student/personal_center/my_message.html', context)


# 学生个人中心-个人信息
def personal_center_stu_info(request):
	context = {}
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info
	# 是否有基本信息修改
	flag = 0
	change_info = models.temp_stu_basic_info.objects.filter(stu_number=request.session['user_number'])
	if len(change_info) > 0:
		flag = 1
	context['change_flag'] = flag
	return render(request, 'student/personal_center/my_info.html', context)


# 学生个人中心-奖项
def personal_center_stu_award(request):
	context = {}
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info
	return render(request, 'student/personal_center/my_award.html', context)


# 学生个人中心-我的经历
def personal_center_stu_experience(request):
	context = {}
	# 获取图片
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info
	return render(request, 'student/personal_center/my_experience.html', context)


# 学生个人中心-查看报名详情
def stu_apply_detail(request):
	context = {}
	com_id = request.GET.get('p1')
	group_id = request.GET.get('p2')
	
	temp = competition_model.temp_com_group_basic_info.objects.filter(group_id=group_id)
	flag = 0
	if len(temp) > 0:
		flag = 1
	context['change'] = flag

	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	com_info.update_status()
	group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)
	depart_list = all_model.depart_info.objects.all()

	info_list = get_object_or_404(competition_model.com_need_info, com_id=com_id)
	stu_list = models.com_stu_info.objects.filter(group_id=group_info)
	teach_list = teacher_model.com_teach_info.objects.filter(group_id=group_info)
	sort_list = competition_model.com_sort_info.objects.filter(com_id=com_info)

	# 判断修改情况
	leader = ""
	flag = 0
	change_flag = 0
	for stu in stu_list:
		# print(stu)
		if stu.stu_id.stu_number == request.session['user_number']:
			if stu.status == '0':
				change_flag = 1
		if stu.is_leader == 1:
			leader = stu
	if leader.stu_id.stu_number == request.session['user_number']:
		flag = 1

	context['change_flag'] = change_flag
	context['modify_flag'] = flag
	context['info_list'] = info_list
	context['stu_list'] = stu_list
	context['teach_list'] = teach_list
	context['sort_list'] = sort_list
	context['group_info'] = group_info
	context['depart_list'] = depart_list
	return render(request, 'student/personal_center/apply_detail.html', context)


# 学生个人中心-修改报名信息
def stu_apply_edit(request):
	context = {}
	com_id = request.GET.get('p1')
	group_id = request.GET.get('p2')
	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	com_info.update_status()
	group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)
	depart_list = all_model.depart_info.objects.all()

	info_list = get_object_or_404(competition_model.com_need_info, com_id=com_id)
	stu_list = models.com_stu_info.objects.filter(group_id=group_info)
	teach_list = teacher_model.com_teach_info.objects.filter(group_id=group_info)
	sort_list = competition_model.com_sort_info.objects.filter(com_id=com_info)

	context['info_list'] = info_list
	context['stu_list'] = stu_list
	context['teach_list'] = teach_list
	context['sort_list'] = sort_list
	context['group_info'] = group_info
	context['depart_list'] = depart_list

	if request.method == 'POST':
		num = com_info.num_stu
		flag_full = com_info.need_full
		flag_same = com_info.same_stu
		flag_proname = info_list.product_name
		flag_teanum = com_info.num_teach
		flag_group = info_list.com_group
		flag_else = info_list.else_info
		flag_groupname = info_list.group_name

		stu_list = []
		for i in range(1, num + 1):
			name = str("stu_num" + str(i))
			temp = request.POST.get(name)
			temp = temp.strip()
			if temp:
				stu_list.append(temp)

		# print(stu_list)

		stu_info_list = []
		for stu in stu_list:
			try:
				name = models.stu_basic_info.objects.get(stu_number=stu)
			except ObjectDoesNotExist:
				context['message'] = '无法搜索到学号对应学生信息，请确认学号无误'
				return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
			else:
				stu_info_list.append(name)

		# 判断是够重复报名
		flag = 1
		if flag_same == 0:
			for stu in stu_info_list:
				com_list = models.com_stu_info.objects.filter(stu_id=stu)
				for com in com_list:
					if com.com_id == com_info and com.group_id != group_info:
						flag = 0
						break
		elif flag_same == 1:
			num = 1
			for stu in stu_info_list:
				com_list = models.com_stu_info.objects.filter(stu_id=stu)
				if num == 1:
					for com in com_list:
						if com.com_id == com_info and com.group_id != group_info:
							flag = 0
							break
				else:
					for com in com_list:
						if com.com_id == com_info and com.is_leader == 1 and com.group_id != group_info:
							flag = 0
							break
				num = num + 1
		if flag == 0:
			# 回到first页面
			context['message'] = '参赛成员不符合规定哦 :('
			return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
		# 判断满员
		student_num = com_info.num_stu
		len_stu = len(stu_info_list)
		if flag_full == 1:
			if len_stu != student_num:
				context['message'] = "人数不符合规定"
				return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
		# 判断学号重复
		list1 = stu_info_list
		list2 = list(set(list1))
		if len(list1) != len(list2):
			# 回到first页面
			context['message'] = '有重复人员的哦 :('
			return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
		# 判断作品名称是否为空
		if flag_proname == 1:
			prodect_name = request.POST.get('product_name')
			prodect_name = prodect_name.strip()
			if prodect_name == "":
				context['message'] = "作品名称没有填哦 X D "
				return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
		# 判断小组名称是否为空
		if flag_groupname == 1:
			group_name = request.POST.get('group_name')
			group_name = group_name.strip()
			if not group_name:
				context['message'] = "小组名称没有填哦 X D "
				return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
		# 获取教师信息
		teach_list = []
		if flag_teanum:
			for i in range(1, flag_teanum + 1):
				teach = request.POST.get(str('tea_name' + str(i))).strip()
				teacher = teacher_model.teach_basic_info.objects.get(tea_number=teach)
				if not teacher:
					context['message'] = "指导教师信息不正确哦 X D "
					return redirect('/student/stu_apply_detail?p1=' + com_id + '&p2=' + group_id)
				else:
					teach_list.append(teacher)
		# 对组别信息进行判断
		if flag_group == 1:
			sort = request.POST.get("sort")
		# 备注信息
		if flag_else == 1:
			else_info = request.POST.get("else_info")
		if flag_proname == 1:
			product_name = request.POST.get('product_name').strip()

		pre_group_info = competition_model.com_group_basic_info.objects.get(group_id=group_info.group_id)
		# 报名中 - 直接修改
		if pre_group_info.status == '0':
			pre_stu_list = models.com_stu_info.objects.filter(group_id=group_info)
			for pre_stu in pre_stu_list:
				pre_stu.delete()
			pre_teach_list = teacher_model.com_teach_info.objects.filter(group_id=group_info)
			for pre_teach in pre_teach_list:
				pre_teach.delete()
			pre_group_info.delete()
			com_group = competition_model.com_group_basic_info()
			com_group.com_id = com_info
			if flag_groupname == 1:
				com_group.group_name = group_name
			com_group.group_num = len_stu
			if flag_group == 1:
				sort_list = competition_model.com_sort_info.objects.filter(com_id=com_info, sort_name=sort)
				com_group.com_group = sort_list[0]
			# 作品名字
			if flag_proname == 1:
				com_group.product_name = product_name
			# 备注
			if flag_else == 1:
				com_group.else_info = else_info
			com_group.save()
			now_group_id = com_group.group_id
			number = 1
			for i in stu_info_list:
				stu = models.com_stu_info()
				stu.com_id = com_info
				stu.group_id = get_object_or_404(competition_model.com_group_basic_info, group_id=now_group_id)
				stu.stu_id = i
				if number == 1:
					stu.is_leader = 1
				number += 1
				stu.save()
			for i in teach_list:
				teach = teacher_model.com_teach_info()
				teach.com_id = com_info
				teach.group_id = get_object_or_404(competition_model.com_group_basic_info, group_id=now_group_id)
				teach.teach_id = i
				teach.save()
			return redirect('/student/personal_center_stu_apply/')
		# 其他状态 - 提交申请
		else:
			temp_group = competition_model.temp_com_group_basic_info()
			temp_group.temp_type = "报名信息"
			temp_group.group_id = group_info
			temp_group.com_id = com_info
			if flag_groupname == 1:
				temp_group.group_name = group_name
				temp_group.group_num = len_stu
			if flag_group == 1:
				sort_list = competition_model.com_sort_info.objects.filter(com_id=com_info, sort_name=sort)
				temp_group.com_group = sort_list[0]
			# 作品名字
			if flag_proname == 1:
				temp_group.product_name = product_name
			# 备注
			if flag_else == 1:
				temp_group.else_info = else_info
			temp_group.apply_type = '1'
			temp_group.save()

			temp_id = temp_group.temp_id

			number = 1
			leader_id = 0
			for i in stu_info_list:
				stu = models.temp_com_stu_info()
				stu.temp_id = get_object_or_404(competition_model.temp_com_group_basic_info, temp_id=temp_id)
				stu.stu_id = i
				if number == 1:
					stu.is_leader = 1
					leader_id = stu.stu_id.stu_number
				number += 1
				stu.save()

			for i in teach_list:
				teach = teacher_model.temp_com_teach_info()
				teach.temp_id = get_object_or_404(competition_model.temp_com_group_basic_info, temp_id=temp_id)
				teach.teach_id = i
				teach.save()

			# 申请修改小组信息
			title = '参赛信息修改申请'
			content = '您已成功提交关于' + com_info.com_name + '的参赛信息修改申请，请等待学科委员审核。'
			send_stu_inform(leader_id, title, content)

			return redirect('/student/personal_center_stu_apply/')
	return render(request, 'student/personal_center/stu_apply_edit.html', context)


# 学生个人中心-撤销报名
def delete_apply(request):
	context = {}
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	img_path = stu_info.photo
	context['stu_name'] = stu_info.stu_name
	context['stu_num'] = stu_info.stu_number
	context['photo'] = img_path

	com_id = request.GET.get('p1')
	group_id = request.GET.get('p2')
	kind = request.GET.get('p3')

	com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
	group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)

	if kind == '1':
		stu_id_list = models.com_stu_info.objects.filter(group_id=group_info, com_id=com_info)
		for stu in stu_id_list:
			if stu.status == '1' and stu.stu_id != stu_info:
				stu_id = stu.stu_id.stu_number
				title = "报名撤销通知"
				content = stu_info.stu_name + '撤销了关于' + com_info.com_name + '的报名，请重新选择成员后重新报名。'
				send_stu_inform(stu_id, title, content)
		stu_id_list.delete()

		teach_id_list = teacher_model.com_teach_info.objects.filter(group_id=group_info, com_id=com_info)
		for teach in teach_id_list:
			if teach.status == '1':
				teach_id = teach.teach_id.tea_number
				title = "报名撤销通知"
				content = stu_info.stu_name + '撤销了关于' + com_info.com_name + '的报名。'
				send_teach_inform(teach_id, title, content)
		teach_id_list.delete()

		com_group = competition_model.com_group_basic_info.objects.filter(group_id=int(group_id), com_id=com_info)
		com_group.delete()
	elif kind != '1':
		temp_apply = competition_model.temp_com_group_basic_info()
		temp_apply.group_id = group_info
		temp_apply.com_id = com_info

		com_group_list = competition_model.com_group_basic_info.objects.filter(group_id=int(group_id), com_id=com_info)
		for i in com_group_list:
			com_group = i
		temp_apply.group_name = com_group.group_name
		temp_apply.group_num = com_group.group_num
		temp_apply.com_group = com_group.com_group
		temp_apply.product_name = com_group.product_name
		temp_apply.else_info = com_group.else_info
		temp_apply.apply_type = '2'
		temp_apply.save()

		stu_list = student_model.com_stu_info.objects.filter(com_id=com_info, group_id=group_info)
		for stu in stu_list:
			student_model.temp_com_stu_info.objects.create(temp_id=temp_apply, stu_id=stu.stu_id,
			                                               is_leader=stu.is_leader)

		teach_list = teacher_model.com_teach_info.objects.filter(com_id=com_info, group_id=group_info)
		for teach in teach_list:
			teacher_model.temp_com_teach_info.objects.create(temp_id=temp_apply, teach_id=teach.teach_id)

		stu_id = stu_info.stu_number
		title = '报名撤销申请'
		content = '你已成功提交关于' + com_info.com_name + '的报名撤销申请,请等待学科委员确认。'
		send_stu_inform(stu_id, title, content)

	return redirect('/student/personal_center_stu_apply')


# 修改密码
def edit_pwd(request):
	context = {}
	stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
	context['stu_info'] = stu_info

	if request.method == 'POST':
		user_info = get_object_or_404(all_model.user_login_info, account=request.session['user_number'])
		pre_pwd = request.POST.get('pre_pwd')
		new_pwd = request.POST.get('new_pwd_2')

		if user_info.psword != pre_pwd:
			context['message'] = "原密码不正确!"
			return render(request, 'student/personal_center/edit_pwd.html', context)

		user_info.psword = new_pwd
		user_info.save()
		return redirect('/student/personal_center_stu_info/')

	return render(request, 'student/personal_center/edit_pwd.html', context)
