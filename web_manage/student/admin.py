from django.contrib import admin
from .models import stu_basic_info, com_stu_info, temp_com_stu_info, stu_fllow_com_info, stu_inform


# Register your models here.
@admin.register(stu_basic_info)
class stu_basic_info_Admin(admin.ModelAdmin):
	list_display = (
		'stu_number', 'stu_name', 'department', 'major', 'grade', 'stu_class', 'sex', 'ID_number', 'bank_number',
		'phone_number', 'email', 'photo', 'stu_card_photo',)


@admin.register(com_stu_info)
class com_stu_info_Admin(admin.ModelAdmin):
	list_display = ('com_id', 'group_id', 'stu_id', 'is_leader',)


@admin.register(temp_com_stu_info)
class temp_com_stu_info_Admin(admin.ModelAdmin):
	list_display = ('temp_id', 'stu_id', 'is_leader',)


@admin.register(stu_fllow_com_info)
class stu_fllow_com_info_Admin(admin.ModelAdmin):
	list_display = ('stu_id', 'com_id', 'status',)


@admin.register(stu_inform)
class stu_inform_Admin(admin.ModelAdmin):
	list_display = ('Recipient_acc', 'From_acc', 'title', 'content', 'create_time')
