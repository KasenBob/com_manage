from django.urls import path
from . import views

# start with blog
urlpatterns = [
	# http://localhost:8000/news/
	path('news_list/', views.news_list, name='news_list'),
	path('news_detail/', views.news_detail, name='news_detail'),
	path('informs_list/', views.informs_list, name='informs_list'),
	path('informs_detail/', views.informs_detail, name='informs_detail'),
]
