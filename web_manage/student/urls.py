from django.urls import path
from . import views

urlpatterns = [
    # 修改密码
    path('edit_pwd/', views.edit_pwd, name='edit_pwd'),
    # 修改个人信息
    path('alter_info_stu/', views.alter_info_stu, name='alter_info_stu'),
    path('alter_notness_info_stu/', views.alter_notness_info_stu, name='alter_notness_info_stu'),
    path('alter_ness_info_stu/', views.alter_ness_info_stu, name='alter_ness_info_stu'),
    # 报名操作
    path('verify_apply/', views.verify_apply, name='verify_apply'),
    path('delete_apply/', views.delete_apply, name='delete_apply'),
    path('stu_apply_edit/', views.stu_apply_edit, name='stu_apply_edit'),
    path('stu_apply_detail/', views.stu_apply_detail, name='stu_apply_detail'),
    path('alter_avatar/', views.alter_avatar, name='alter_avatar'),
    # 个人中心
    path('personal_center_stu_apply/', views.personal_center_stu_apply, name='personal_center_stu_apply'),
    path('personal_center_stu_message/', views.personal_center_stu_message, name='personal_center_stu_message'),
    path('message_detail/', views.message_detail, name='message_detail'),
    path('personal_center_stu_info/', views.personal_center_stu_info, name='personal_center_stu_info'),
    path('personal_center_stu_experience/', views.personal_center_stu_experience,
         name='personal_center_stu_experience'),
    path('verify_not_apply/', views.verify_not_apply, name='verify_not_apply'),
]
