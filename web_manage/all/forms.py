from django import forms
from .models import Article


class ArticleForm(forms.Form):
	class Meta:
		# 指明数据模型来源
		model = Article
		# 定义表单包含的字段
		fields = ('content')
