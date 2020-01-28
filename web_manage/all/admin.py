from django.contrib import admin
from .models import depart_info, major_info, grade_info, class_info, user_login_info, Article, inform


# Register your models here.
@admin.register(depart_info)
class depart_info_Admin(admin.ModelAdmin):
	list_display = ('depart_name',)


@admin.register(major_info)
class major_info_Admin(admin.ModelAdmin):
	list_display = ('major_name', 'depart',)


@admin.register(grade_info)
class grade_info_Admin(admin.ModelAdmin):
	list_display = ('grade_name',)


@admin.register(class_info)
class class_info_Admin(admin.ModelAdmin):
	list_display = ('class_name',)


@admin.register(user_login_info)
class class_info_Admin(admin.ModelAdmin):
	list_display = ('account', 'psword', 'have_login', 'have_alter', 'ip')


@admin.register(Article)
class Article_Admin(admin.ModelAdmin):
	list_display = ('content',)


@admin.register(inform)
class inform_Admin(admin.ModelAdmin):
	list_display = ('title', 'content', 'author', 'create_time',)
