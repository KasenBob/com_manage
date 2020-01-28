from django.contrib import admin
from .models import com_basic_info, series_info, series_depart, com_sort_info, com_need_info, \
	temp_com_group_basic_info, com_group_basic_info


# Register your models here.
@admin.register(com_basic_info)
class com_basic_info_Admin(admin.ModelAdmin):
	list_display = (
		'com_id', 'com_name', 'series_id', 'begin_regit', 'end_regit', 'begin_time', 'end_time', 'num_stu', 'need_full',
		'same_stu', 'com_sort_num', 'com_web', 'if_web', 'num_teach', 'com_status',)


@admin.register(series_info)
class series_info_Admin(admin.ModelAdmin):
	list_display = ('id', 'name', 'introduction', 'photo', 'now_com_id',)


@admin.register(series_depart)
class series_depart_Admin(admin.ModelAdmin):
	list_display = ('id', 'series_id', 'depart_name',)


@admin.register(com_sort_info)
class com_sort_info_Admin(admin.ModelAdmin):
	list_display = ('id', 'com_id', 'sort_name',)


@admin.register(com_need_info)
class com_need_info_Admin(admin.ModelAdmin):
	list_display = (
		'com_id', 'stu_num', 'stu_name', 'ID_number', 'sex', 'depart', 'major', 'grade', 'stu_class', 'email',
		'phone_num',
		'com_group', 'group_name', 'product_name', 'tea_num', 'bank_number', 'else_info',)


@admin.register(temp_com_group_basic_info)
class temp_com_group_basic_info_Admin(admin.ModelAdmin):
	list_display = (
		'temp_id', 'group_id', 'com_id', 'group_name', 'group_num', 'com_group', 'product_name', 'else_info',
		'apply_type',)


@admin.register(com_group_basic_info)
class com_group_basic_info_Admin(admin.ModelAdmin):
	list_display = (
		'group_id', 'com_id', 'group_name', 'group_num', 'com_group', 'product_name', 'else_info',)
