from django.contrib import admin
from .models import news


# Register your models here.
@admin.register(news)
class news_Admin(admin.ModelAdmin):
	list_display = ('title', 'content', 'author', 'created_time', 'last_update_time')
