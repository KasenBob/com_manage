from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.conf import settings
from datetime import datetime
from django.core.paginator import Paginator
import json
from django.core import serializers
from . import models
import os
import all.models as all_model
import competition.models as competition_model
import teacher.models as teacher_model
import student.models as student_model
from .tasks import send_stu_inform
from teacher.tasks import send_teach_inform
from competition.views import verify_all_apply


# Create your views here.
# 学生修改个人信息-非基础信息
def alter_notness_info_stu(request):
    context = {}
    nid = request.session.get('user_number', None)
    stu_info = get_object_or_404(models.stu_basic_info, stu_number=nid)
    if request.method == "POST":
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        bank_number = request.POST.get("bank_number")
        stu_info.bank_number = bank_number
        stu_info.phone_number = phone_number
        stu_info.email = email
        stu_info.save()
    return redirect("/student/personal_center_stu_info/")


# 学生修改个人信息-基础信息
def alter_ness_info_stu(request):
    context = {}
    nid = request.session.get('user_number', None)
    stu_info = get_object_or_404(models.stu_basic_info, stu_number=nid)
    depart_info = all_model.depart_info.objects.all()
    major_info = all_model.major_info.objects.all()
    grade_info = all_model.grade_info.objects.all()
    class_info = all_model.class_info.objects.all()
    # 是否有基本信息修改
    flag = 0
    change_info = models.temp_stu_basic_info.objects.filter(stu_number=stu_info)
    if len(change_info) > 0:
        flag = 1
        context['change_stu'] = change_info[0]
    context['change_flag'] = flag
    # 基本信息
    context['stu_info'] = stu_info
    context['depart_info'] = depart_info
    context['major_info'] = major_info
    context['grade_info'] = grade_info
    context['class_info'] = class_info

    if request.method == "POST":
        # 需要验证（信息是否错误；是否有修改）
        temp_stu = models.temp_stu_basic_info()
        temp_stu.stu_name = stu_info.stu_name
        temp_stu.stu_number = stu_info
        temp_stu.ID_number = request.POST.get("ID_number")
        temp_stu.sex = request.POST.get("sex")
        temp_stu.department = get_object_or_404(all_model.depart_info, depart_name=request.POST.get('depart'))
        temp_stu.major = get_object_or_404(all_model.major_info, major_name=request.POST.get('major'))
        temp_stu.grade = get_object_or_404(all_model.grade_info, grade_name=request.POST.get('grade'))
        temp_stu.stu_class = get_object_or_404(all_model.class_info, class_name=request.POST.get('stu_class'))
        temp_stu.save()
        # 发送通知
        stu_id = stu_info.stu_number
        title = '个人信息修改申请'
        content = '您已成功提交个人信息修改申请，请等待学科委员审核。'
        send_stu_inform(stu_id, title, content)
        return  redirect('/student/personal_center_stu_info/')

    return render(request, 'student/personal_center/my_info_edit.html', context)


# 学生修改个人信息-初次登录
def alter_info_stu(request):
    context = {}
    nid = request.session.get('user_number', None)
    user_info = get_object_or_404(all_model.user_login_info, account=nid)
    stu_info = get_object_or_404(models.stu_basic_info, stu_number=nid)
    depart_info = all_model.depart_info.objects.all()
    major_info = all_model.major_info.objects.all()
    grade_info = all_model.grade_info.objects.all()
    class_info = all_model.class_info.objects.all()
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
            return render(request, 'student/personal_center/alter_info.html', context)

        if ID_number == None or ID_number == "" or ID_number == 'None':
            context['message'] = "请务必填写身份证号！"
            return render(request, 'student/personal_center/alter_info.html', context)

        bank_number = request.POST.get('bank_number')
        phone_number = request.POST.get('phone_number')

        if phone_number == None or phone_number == "" or phone_number == 'None':
            context['message'] = "请务必填写手机号码！"
            return render(request, 'student/personal_center/alter_info.html', context)

        email = request.POST.get('email')

        if email == None or email == "" or email == 'None':
            context['message'] = "请务必填写邮箱！"
            return render(request, 'student/personal_center/alter_info.html', context)

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


# 学生个人中心-竞赛
def personal_center_stu_apply(request):
    context = {}
    stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
    apply_lists = models.com_stu_info.objects.filter(stu_id=stu_info).order_by('-group_id')
    apply_list = []
    flags = []
    for apply in apply_lists:
        if apply.com_id.com_status != '3':
            apply_list.append(apply)
            # flag{"0:成功", "1:待老师确认", "2:待成员确认", "3:组队待确认", "4:修改审核中", "5:撤销审核中"}
            # 初始化flag
            flag = -1
            # 成功
            if apply.group_id.status == '1':
                flag = 0
            else:
                if flag == -1:
                    # 待教师确认
                    teach_apply_lists = teacher_model.com_teach_info.objects.filter(group_id=apply.group_id)
                    for teach_apply in teach_apply_lists:
                        if teach_apply.status == '0':
                            flag = 1
                            break
                if flag == -1:
                    # 待成员确认
                    if apply.is_leader == 1:
                        stu_apply_lists = models.com_stu_info.objects.filter(group_id=apply.group_id)
                        for stu_apply in stu_apply_lists:
                            if stu_apply.status == '0':
                                flag = 2
                                break
                    # 组队待确认
                    else:
                        if apply.status == '0':
                            flag = 3
                if flag == -1:
                    temp_apply_lists = competition_model.temp_com_group_basic_info.objects.filter(
                        group_id=apply.group_id).order_by("created_time")
                    # 待审核
                    for temp_apply in temp_apply_lists:
                        if temp_apply.apply_type == '1':
                            flag = 4
                        elif temp_apply.apply_type == '2':
                            flag = 5
            flags.append(flag)
    # 打包标志和小组信息
    applys = zip(flags, apply_list)

    context['apply_list'] = applys

    return render(request, 'student/personal_center/my_apply.html', context)


# 学生个人中心-消息
def personal_center_stu_message(request):
    context = {}

    stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
    informs_list = models.stu_inform.objects.filter(
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
    return render(request, 'student/personal_center/my_message.html', context)


# 学生个人中心-个人信息-查看详情
def message_detail(request):
    context = {}
    inform_id = request.GET.get("p")
    inform = get_object_or_404(models.stu_inform, pk=inform_id)
    context['inform'] = inform.content
    return JsonResponse(context)


# 学生个人中心-个人信息
def personal_center_stu_info(request):
    context = {}
    stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
    context['stu_info'] = stu_info
    return render(request, 'student/personal_center/my_info.html', context)


# 学生个人中心-参赛历史
def personal_center_stu_experience(request):
    context = {}
    stu_info = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
    award_lists = models.com_stu_award.objects.all()
    context['award_list'] = award_lists
    return render(request, 'student/personal_center/my_experience.html', context)


# 学生个人中心-查看报名详情
def stu_apply_detail(request):
    context = {}
    group_id = request.GET.get('p')
    group_info = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)
    user = get_object_or_404(models.stu_basic_info, stu_number=request.session['user_number'])
    user_apply = models.com_stu_info.objects.filter(group_id=group_info, stu_id=user)
    user_apply = user_apply[0]
    com_info = get_object_or_404(competition_model.com_basic_info, com_id=group_info.com_id.com_id)
    # 竞赛名称
    context['com_name'] = com_info.com_name
    context['com_id'] = com_info.com_id
    context['group_id'] = group_id
    # 比赛类型
    context['type'] = com_info.type
    # 参赛学生
    stu_apply_lists = models.com_stu_info.objects.filter(group_id=group_info)
    leader = ""
    member_list = []
    if context['type'] == '1':
        for stu in stu_apply_lists:
            if stu.is_leader == 1:
                leader = stu.stu_id.stu_name
            else:
                member_list.append(stu.stu_id.stu_name)
        # 团队赛-队长和成员
        context['leader'] = leader
        member_list = json.loads(serializers.serialize('json', member_list))
        context['member_list'] = member_list
    else:
        # 个人赛
        context['member'] = user_apply.stu_id.stu_name
    # 指导教师
    teach_apply_lists = teacher_model.com_teach_info.objects.filter(group_id=group_info)
    teach_list = []
    for teach in teach_apply_lists:
        teach_list.append(teach.teach_id.tea_name)
    context['teach_list'] = teach_list
    # 判断状态
    apply_status = user_apply.status
    status = -1
    # 单人赛-未成功：0；
    # 单人赛-已成功-无修改：1； 单人赛-已成功-有修改：2；
    # 团队赛-不是队长-未确认：3； 团队赛-不是队长-已确认：4；
    # 团队赛-是队长-未成功：5；
    # 团队赛-是队长-已成功-未修改：6； 团队赛-是队长-已成功-有修改：7；
    if context['type'] == '0':
        if group_info.status == '0':
            status = 0
        else:
            temp_apply = competition_model.temp_com_group_basic_info.objects.filter(group_id=group_info)
            if len(temp_apply) == 0:
                status = 1
            elif len(temp_apply) > 0:
                status = 2
    else:
        if user_apply.is_leader == 0:
            if user_apply.status == '0':
                status = 3
            elif user_apply.status == '1':
                status = 4
        elif user_apply.is_leader == 1:
            if group_info.status == '0':
                status = 5
            else:
                temp_apply = competition_model.temp_com_group_basic_info.objects.filter(group_id=group_info)
                if len(temp_apply) == 0:
                    status = 6
                elif len(temp_apply) > 0:
                    status = 7
    context['status'] = status
    # context = json.loads(serializers.serialize('json', context))
    return JsonResponse(context)


# 学生个人中心-确认报名邀请
def verify_apply(request):
    context = {}
    group_id = request.GET.get('p2')
    group = get_object_or_404(competition_model.com_group_basic_info, group_id=group_id)
    # 获取学生比赛信息
    stu = get_object_or_404(student_model.stu_basic_info, stu_number=request.session['user_number'])
    com_stu_list = student_model.com_stu_info.objects.filter(group_id=group, stu_id=stu)
    com_stu = com_stu_list[0]
    com_stu.status = '1'
    com_stu.save()
    # 检查小组确认情况
    verify_all_apply(group_id)
    # 团队赛，若非队长则确认后向队长发送确认信息
    if com_stu.is_leader != 1:
        com_stu_list = student_model.com_stu_info.objects.filter(group_id=group)
        for com_stu in com_stu_list:
            if com_stu.is_leader == 1:
                stu_id = com_stu.stu_id.stu_number
                title = '报名进度通知'
                content = stu.stu_name + '已确认关于' + group.com_id.com_name + '的组队邀请。'
                send_stu_inform(stu_id, title, content)
                break
    return redirect('/student/personal_center_stu_apply')


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

    temp_group_list = competition_model.temp_com_group_basic_info.objects.filter(group_id=group_info).order_by("-created_time")
    change_flag = 0
    if len(temp_group_list) > 0:
        change_flag = 1
        context['change_group'] = temp_group_list[0]
    context['change_flag'] = change_flag

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

        stu_info_list = []
        for stu in stu_list:
            name = models.stu_basic_info.objects.get(stu_number=stu)
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
            return render(request, 'student/personal_center/stu_apply_edit.html', context)
        # 判断满员
        student_num = com_info.num_stu
        len_stu = len(stu_info_list)
        if flag_full == 1:
            if len_stu != student_num:
                context['message'] = "人数不符合规定"
                return render(request, 'student/personal_center/stu_apply_edit.html', context)
        # 判断学号重复
        list1 = stu_info_list
        list2 = list(set(list1))
        if len(list1) != len(list2):
            # 回到first页面
            context['message'] = '有重复人员的哦 :('
            return render(request, 'student/personal_center/stu_apply_edit.html', context)
        # 判断作品名称是否为空
        if flag_proname == 1:
            prodect_name = request.POST.get('product_name')
            prodect_name = prodect_name.strip()
            if prodect_name == "":
                context['message'] = "作品名称没有填哦 X D "
                return render(request, 'student/personal_center/stu_apply_edit.html', context)
        # 判断小组名称是否为空
        if flag_groupname == 1:
            group_name = request.POST.get('group_name')
            group_name = group_name.strip()
            if not group_name:
                context['message'] = "小组名称没有填哦 X D "
                return render(request, 'student/personal_center/stu_apply_edit.html', context)
        # 获取教师信息
        teach_list = []
        if flag_teanum:
            for i in range(1, flag_teanum + 1):
                teach = request.POST.get(str('tea_name' + str(i))).strip()
                teacher = teacher_model.teach_basic_info.objects.get(tea_number=teach)
                if not teacher:
                    context['message'] = "指导教师信息不正确哦 X D "
                    return render(request, 'student/personal_center/stu_apply_edit.html', context)
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
