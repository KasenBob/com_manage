from django.urls import path
from . import views

urlpatterns = [
	path('series_list/', views.series_list, name='series_list'),
	path('com_list/', views.com_list, name='com_list'),
	path('com_detail/', views.com_detail, name='com_detail'),
	path('com_attach_download/', views.com_attach_download, name='com_attach_download'),
	path('com_apply_first/', views.com_apply_first, name='com_apply_first'),
	path('com_apply_second/', views.com_apply_second, name='com_apply_second'),
	path('verify_apply/', views.verify_apply, name='verify_apply'),
	path('select_mate_first/', views.select_mate_first, name='select_mate_first'),
	path('select_mate_second/', views.select_mate_second, name='select_mate_second'),
]