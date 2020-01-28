from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.conf import settings
from . import models
import all.models as all_model


# Create your views here.
def news_list(request):
	context = {}
	news_list = models.news.objects.all()
	paginator = Paginator(news_list, 3)  # 每?篇进行分页
	page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
	page_of_news = paginator.get_page(page_num)
	current_page_num = page_of_news.number  # 获取当前页码
	# 获取当前前后各两页的页码范围
	page_range = list(range(max(current_page_num - 1, 1), current_page_num)) + \
	             list(range(current_page_num, min(current_page_num + 1, paginator.num_pages) + 1))
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
	context['news_list'] = news_list
	return render(request, 'news/news/news_list.html', context)


def news_detail(request):
	context = {}
	news_id = request.GET.get('p')
	news = get_object_or_404(models.news, pk=news_id)
	context['news'] = news
	return render(request, 'news/news/news_detail.html', context)


def informs_list(request):
	context = {}

	inform_list = all_model.inform.objects.all().order_by('-create_time')

	paginator = Paginator(inform_list, 10)  # 每?篇进行分页
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

	return render(request, 'informs/informs_list.html', context)


def informs_detail(request):
	context = {}
	inform_id = request.GET.get('p')
	inform = get_object_or_404(all_model.inform, pk=inform_id)
	context['inform'] = inform
	return render(request, 'informs/informs_detail.html', context)