from django.urls import path
from . import views

urlpatterns = [
	path('edit_pwd/', views.edit_pwd, name='edit_pwd'),
	path('alter_info_stu/', views.alter_info_stu, name='alter_info_stu'),
	path('delete_apply/', views.delete_apply, name='delete_apply'),
	path('stu_apply_edit/', views.stu_apply_edit, name='stu_apply_edit'),
	path('stu_apply_detail/', views.stu_apply_detail, name='stu_apply_detail'),
	path('alter_avatar/', views.alter_avatar, name='alter_avatar'),
	path('personal_center_stu_apply/', views.personal_center_stu_apply, name='personal_center_stu_apply'),
	path('personal_center_stu_message/', views.personal_center_stu_message, name='personal_center_stu_message'),
	path('personal_center_stu_info/', views.personal_center_stu_info, name='personal_center_stu_info'),
	path('personal_center_stu_award/', views.personal_center_stu_award, name='personal_center_stu_award'),
	path('personal_center_stu_experience/', views.personal_center_stu_experience,
	     name='personal_center_stu_experience'),
]
