from django.urls import path
from . import views

urlpatterns = [
	path('edit_pwd/', views.edit_pwd, name='edit_pwd'),
	path('alter_info_teach/', views.alter_info_teach, name='alter_info_teach'),
	path('personal_center_teach_info/', views.personal_center_teach_info, name='personal_center_teach_info'),
	path('personal_center_teach_apply/', views.personal_center_teach_apply, name='personal_center_teach_apply'),
	path('personal_center_teach_team/', views.personal_center_teach_team, name='personal_center_teach_team'),
	path('personal_center_teach_experience/', views.personal_center_teach_experience,
	     name='personal_center_teach_experience'),
	path('personal_center_teach_message/', views.personal_center_teach_message, name='personal_center_teach_message'),
	path('personal_center_teach_award/', views.personal_center_teach_award, name='personal_center_teach_award'),
	path('personal_center_teach_record/', views.personal_center_teach_record, name='personal_center_teach_record'),
	path('teach_apply_deatil/', views.teach_apply_deatil, name='teach_apply_deatil'),
	path('reject_apply/', views.reject_apply, name='reject_apply'),
	path('confirm_apply/', views.confirm_apply, name='confirm_apply'),
	path('alter_avatar/', views.alter_avatar, name='alter_avatar'),
]
