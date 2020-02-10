from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.conf import settings
import datetime
from . import models
import json
from django.core import serializers
import os
import all.models as all_model
import competition.models as competition_model
import student.models as student_model
from .tasks import send_teach_inform
from student.tasks import send_stu_inform


# Create your views here.
# 修改头像
def alter_avatar(request):
    context = {}
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=request.session['user_number'])
    context['teach_info'] = teach_info
    if request.method == "POST":
        photo = request.FILES.get("avatar_file")
        if photo != None:
            f_name = photo.name
            f_name = f_name.split('.')[-1].lower()
            # 重命名照片
            teach_info.photo = "teach_photo/" + teach_info.tea_number + "/" + 'head' + '.' + f_name
            url = settings.MEDIA_ROOT + 'teach_photo/' + teach_info.tea_number
            # 判断路径是否存在
            isExists = os.path.exists(url)
            if not isExists:
                os.makedirs(url)
            photo_url = open(
                settings.MEDIA_ROOT + "teach_photo/" + teach_info.tea_number + "/" + 'head' + '.' + f_name,
                'wb')
            for chunk in photo.chunks():
                photo_url.write(chunk)
            photo_url.close()
            teach_info.save()
        return redirect('/teacher/alter_avatar/')
    return render(request, 'teacher/personal_center/alter_avatar.html', context)


# 教师修改个人信息-非基础信息
def alter_notness_info_teach(request):
    context = {}
    nid = request.session.get('user_number', None)
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=nid)
    if request.method == "POST":
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        teach_info.phone_number = phone_number
        teach_info.email = email
        teach_info.save()
    return redirect("/teacher/personal_center_teach_info/")


# 教师修改个人信息-基础信息
def alter_ness_info_teach(request):
    context = {}
    nid = request.session.get('user_number', None)
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=nid)
    depart_info = all_model.depart_info.objects.all()
    profess_info = models.profess_info.objects.all()
    # 是否有基本信息修改
    flag = 0
    change_info = models.temp_teach_basic_info.objects.filter(teach_number=teach_info)
    if len(change_info) > 0:
        flag = 1
        context['change_teacher'] = change_info[0]
    context['change_flag'] = flag
    # 基本信息
    context['teach_info'] = teach_info
    context['depart_info'] = depart_info
    context['profess_info'] = profess_info

    if request.method == "POST":
        # 需要验证（信息是否错误；是否有修改）
        temp_teach = models.temp_teach_basic_info()
        temp_teach.tea_name = teach_info.tea_name
        temp_teach.teach_number = teach_info
        temp_teach.department = get_object_or_404(all_model.depart_info, depart_name=request.POST.get('depart'))
        temp_teach.profess = get_object_or_404(models.profess_info, profess_name=request.POST.get('profess'))
        temp_teach.save()
        # 发送通知
        teach_id = teach_info.tea_number
        title = '个人信息修改申请'
        content = '您已成功提交个人信息修改申请，请等待学科委员审核。'
        send_teach_inform(teach_id, title, content)
        return redirect('/teacher/personal_center_teach_info/')

    return render(request, 'teacher/personal_center/my_info_edit.html', context)


# 教师修改个人信息
def alter_info_teach(request):
    context = {}
    nid = request.session.get('user_number', None)
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=nid)
    user_info = get_object_or_404(all_model.user_login_info, account=nid)
    profess_info = models.profess_info.objects.all()
    depart_info = all_model.depart_info.objects.all()

    context['teach_info'] = teach_info
    context['profess_info'] = profess_info
    context['depart_info'] = depart_info
    context['user_info'] = user_info

    if user_info.have_alter == '0':
        context['message'] = "请确认个人信息无误。"

    if request.method == "POST":
        # tea_number = request.POST.get('tea_number')
        tea_name = request.POST.get('tea_name')
        profess = request.POST.get('profess')
        profess = get_object_or_404(models.profess_info, profess_name=profess)
        department = request.POST.get('department')
        department = get_object_or_404(all_model.depart_info, depart_name=department)
        ID_number = request.POST.get('ID_number')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        if ID_number == 'None' or ID_number == "":
            context['message'] = "请务必填写身份证号！"
            return render(request, 'teacher/personal_center/alter_info_teach.html', context)

        if phone_number == 'None' or phone_number == "":
            context['message'] = "请务必填写手机号码！"
            return render(request, 'teacher/personal_center/alter_info_teach.html', context)

        if email == 'None' or email == "":
            context['message'] = "请务必填写邮箱！"
            return render(request, 'teacher/personal_center/alter_info_teach.html', context)

        photo = request.FILES.get("photo")
        # print(photo)

        tea_info = models.teach_basic_info.objects.get(tea_number=nid)

        flag = 1
        if tea_info.tea_name != tea_name:
            flag = 0
        if tea_info.profess != profess:
            flag = 0
        if tea_info.department != department:
            flag = 0

        if flag == 0:
            temp_teach_info = models.temp_teach_basic_info()
            temp_teach_info.teach_number = tea_info
            temp_teach_info.tea_name = tea_name
            temp_teach_info.profess = profess
            temp_teach_info.department = department
            temp_teach_info.save()
            # 发送通知
            stu_id = tea_info.tea_number
            title = '个人信息修改申请'
            content = '您已成功提交个人信息修改申请，请等待学科委员审核。'
            send_teach_inform(stu_id, title, content)

        # tea_info.tea_number = tea_number
        # tea_info.tea_name = tea_name
        # tea_info.profess = get_object_or_404(models.profess_info, profess_name=profess)
        # tea_info.department = get_object_or_404(all_model.depart_info, depart_name=department)
        tea_info.ID_number = ID_number
        tea_info.phone_number = phone_number
        tea_info.email = email
        tea_info.save()
        # 更改修改状态
        user_login = get_object_or_404(all_model.user_login_info, account=request.session['user_number'])
        user_login.have_login = '1'
        user_login.have_alter = '1'
        user_login.save()

        return redirect('/teacher/personal_center_teach_info')

    return render(request, 'teacher/personal_center/alter_info_teach.html', context)


# 教师个人中心-个人信息
def personal_center_teach_info(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info
    com_apply = models.com_teach_info.objects.filter(status='0', teach_id=teach_info)
    apply_number = len(com_apply)
    context['apply_number'] = apply_number
    return render(request, 'teacher/personal_center/my_info.html', context)


# 教师个人中心-指导申请
def personal_center_teach_apply(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info
    com_apply = models.com_teach_info.objects.filter(status='0', teach_id=teach_info)
    apply_number = len(com_apply)
    context['apply_number'] = apply_number

    # 未确认的指导申请
    temp_com_apply = models.com_teach_info.objects.filter(teach_id=teach_info)
    com_apply = []
    for temp_com in temp_com_apply:
        if temp_com.group_id.status == '0':
            com_apply.append(temp_com)
    # 指导申请发起人
    leader_apply = []
    for apply in com_apply:
        group_id = apply.group_id
        leader = student_model.com_stu_info.objects.filter(group_id=group_id, is_leader=1)
        for i in leader:
            leader_apply.append(i)

    confirm_apply = zip(leader_apply, com_apply)
    context['confirm_apply'] = confirm_apply

    return render(request, 'teacher/personal_center/my_apply.html', context)


# 教师个人中心-参赛小组
def personal_center_teach_team(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info
    com_apply = models.com_teach_info.objects.filter(status='0', teach_id=teach_info)
    apply_number = len(com_apply)
    context['apply_number'] = apply_number

    # 正在参赛小组
    apply_list = models.com_teach_info.objects.filter(teach_id=teach_info.tea_number).order_by('-group_id')

    apply_one_list = []
    apply_all_list = []
    stu_list_one = []
    stu_list_all = []
    for apply in apply_list:
        if apply.com_id.type == '0' and apply.group_id.status == '1':
            apply_one_list.append(apply)
            group = apply.group_id
            stu = get_object_or_404(student_model.com_stu_info, group_id=group)
            stu_list_one.append(stu)
        elif apply.com_id.type == '1' and apply.group_id.status == '1':
            apply_all_list.append(apply)
            group = apply.group_id
            stu = student_model.com_stu_info.objects.filter(group_id=group)
            stu_list_all.append(stu)

    apply_one = zip(apply_one_list, stu_list_one)
    apply_all = zip(apply_all_list, stu_list_all)

    context['apply_one'] = apply_one
    context['apply_all'] = apply_all

    return render(request, 'teacher/personal_center/my_team.html', context)


# 教师个人中心-参赛经历
def personal_center_teach_experience(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info
    com_apply = models.com_teach_info.objects.filter(status='0', teach_id=teach_info)
    apply_number = len(com_apply)
    context['apply_number'] = apply_number
    return render(request, 'teacher/personal_center/my_experience.html', context)


# 教师个人中心-获奖结果
def personal_center_teach_award(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info
    com_apply = models.com_teach_info.objects.filter(status='0', teach_id=teach_info)
    apply_number = len(com_apply)
    context['apply_number'] = apply_number
    return render(request, 'teacher/personal_center/my_award.html', context)


# 教师个人中心-指导记录
def personal_center_teach_record(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info
    com_apply = models.com_teach_info.objects.filter(status='0', teach_id=teach_info)
    apply_number = len(com_apply)
    context['apply_number'] = apply_number
    return render(request, 'teacher/personal_center/my_record.html', context)


# 小组总体报名情况
def verify_all_apply(group_id):
    group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)
    com_stu_list = student_model.com_stu_info.objects.filter(group_id=group_id)
    com_teach_list = models.com_teach_info.objects.filter(group_id=group_id)
    flag = 1
    for com_stu in com_stu_list:
        if com_stu.status == '0':
            flag = 0
            break
    if flag == 1:
        for com_teach in com_teach_list:
            if com_teach.status == '0':
                flag = 0
                break
    if flag == 1:
        group_info.status = '1'
        group_info.save()


# 教师个人中心-确认报名
def confirm_apply(request):
    context = {}
    teach_id = request.session['user_number']
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    com_id = request.GET.get('p1')
    group_id = request.GET.get('p2')
    com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
    group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)

    com_teach_info = models.com_teach_info.objects.filter(teach_id=teach_info, group_id=group_info)
    # print(com_teach_info)
    for com_teach in com_teach_info:
        com_teach.status = '1'
        com_teach.save()

    # 发信息
    com_stu_list = student_model.com_stu_info.objects.filter(group_id=group_info)
    for com_stu in com_stu_list:
        if com_stu.status == '1':
            stu_id = com_stu.stu_id.stu_number
            title = '报名进度通知'
            content = teach_info.tea_name + '教师已确认关于' + com_info.com_name + '的报名申请。'
            send_stu_inform(stu_id, title, content)

    verify_all_apply(group_id)

    return redirect('/teacher/personal_center_teach_apply/')


# 教师个人中心-通知信息
def personal_center_teach_message(request):
    context = {}
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=request.session['user_number'])
    informs_list = models.teach_inform.objects.filter(
        Recipient_acc=get_object_or_404(all_model.user_login_info, account=request.session['user_number'])).order_by(
        '-create_time')

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

    context['page_of_informs'] = page_of_informs
    context['page_range'] = page_range
    context['informs'] = informs_list
    return render(request, 'teacher/personal_center/my_message.html', context)


# 学生个人中心-个人信息-查看详情
def message_detail(request):
    context = {}
    inform_id = request.GET.get("p")
    inform = get_object_or_404(models.teach_inform, pk=inform_id)
    context['inform'] = inform.content
    return JsonResponse(context)


# 教师个人中心-驳回报名
def reject_apply(request):
    context = {}

    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)

    com_id = request.GET.get('p1')
    group_id = request.GET.get('p2')
    com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
    group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)

    stu_id_list = student_model.com_stu_info.objects.filter(group_id=group_info, com_id=com_info)
    for stu in stu_id_list:
        if stu.status == '1':
            stu_id = stu.stu_id.stu_number
            title = '报名驳回通知'
            content = teach_info.tea_name + '教师已驳回关于' + com_info.com_name + '的报名申请，请重新选择指导教师后重新报名。'
            send_stu_inform(stu_id, title, content)
    stu_id_list.delete()

    teach_id_list = models.com_teach_info.objects.filter(group_id=group_info, com_id=com_info)
    teach_id_list.delete()

    com_group = competition_model.com_group_basic_info.objects.filter(group_id=int(group_id), com_id=com_info)
    com_group.delete()

    return redirect('/teacher/personal_center_teach_apply/')


# 教师个人中心-竞赛详情
def teach_apply_deatil(request):
    context = {}
    com_id = request.GET.get('p1')
    group_id = request.GET.get('p2')
    com_info = get_object_or_404(competition_model.com_basic_info, com_id=com_id)
    com_info.update_status()
    group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)
    depart_list = all_model.depart_info.objects.all()

    info_list = get_object_or_404(competition_model.com_need_info, com_id=com_id)
    stu_list = student_model.com_stu_info.objects.filter(group_id=group_info)
    teach_list = models.com_teach_info.objects.filter(group_id=group_info)
    sort_list = competition_model.com_sort_info.objects.filter(com_id=com_info)

    change_flag = 0
    for teach in teach_list:
        if teach.teach_id.tea_number == request.session['user_number']:
            if teach.status == '0':
                change_flag = 1

    context['change_flag'] = change_flag
    context['info_list'] = info_list
    context['stu_list'] = stu_list
    context['teach_list'] = teach_list
    context['sort_list'] = sort_list
    context['group_info'] = group_info
    context['depart_list'] = depart_list
    return render(request, "teacher/personal_center/apply_detail.html", context)


# 修改密码
def edit_pwd(request):
    context = {}
    teach_id = request.session['user_number']
    # 获取教师信息
    teach_info = get_object_or_404(models.teach_basic_info, tea_number=teach_id)
    context['teach_info'] = teach_info

    if request.method == 'POST':
        user_info = get_object_or_404(all_model.user_login_info, account=request.session['user_number'])
        pre_pwd = request.POST.get('pre_pwd')
        new_pwd = request.POST.get('new_pwd_2')

        if user_info.psword != pre_pwd:
            context['message'] = "原密码不正确!"
            return render(request, 'teacher/personal_center/edit_pwd.html', context)

        user_info.psword = new_pwd
        user_info.save()
        return redirect('/teacher/personal_center_teach_info/')

    return render(request, 'teacher/personal_center/edit_pwd.html', context)
