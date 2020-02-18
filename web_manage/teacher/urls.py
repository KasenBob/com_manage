from django.urls import path
from . import views

urlpatterns = [
    # 修改密码
    path('edit_pwd/', views.edit_pwd, name='edit_pwd'),
    # 修改个人信息
    path('alter_info_teach/', views.alter_info_teach, name='alter_info_teach'),
    path('alter_notness_info_teach/', views.alter_notness_info_teach, name='alter_notness_info_teach'),
    path('alter_ness_info_teach/', views.alter_ness_info_teach, name='alter_ness_info_teach'),
    path('message_detail/', views.message_detail, name='message_detail'),
    # 个人中心
    path('personal_center_teach_info/', views.personal_center_teach_info, name='personal_center_teach_info'),
    path('personal_center_teach_apply/', views.personal_center_teach_apply, name='personal_center_teach_apply'),
    path('personal_center_teach_team/', views.personal_center_teach_team, name='personal_center_teach_team'),
    path('apply_list/', views.apply_list, name='apply_list'),
    path('personal_center_teach_experience/', views.personal_center_teach_experience,
         name='personal_center_teach_experience'),
    path('personal_center_teach_message/', views.personal_center_teach_message, name='personal_center_teach_message'),
    path('personal_center_teach_award/', views.personal_center_teach_award, name='personal_center_teach_award'),
    path('personal_center_teach_record/', views.personal_center_teach_record, name='personal_center_teach_record'),
    # 报名操作
    path('teach_apply_deatil/', views.teach_apply_deatil, name='teach_apply_deatil'),
    path('reject_apply/', views.reject_apply, name='reject_apply'),
    path('confirm_apply/', views.confirm_apply, name='confirm_apply'),
    path('alter_avatar/', views.alter_avatar, name='alter_avatar'),
]
