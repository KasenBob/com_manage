from django.contrib import admin
from .models import teach_basic_info, com_teach_info, temp_com_teach_info, teach_inform


# Register your models here.
@admin.register(teach_basic_info)
class teach_basic_info_Admin(admin.ModelAdmin):
	list_display = (
		'tea_number', 'tea_name', 'profess', 'department', 'ID_number', 'email', 'phone_number', 'photo',)


@admin.register(com_teach_info)
class com_teach_info_Admin(admin.ModelAdmin):
	list_display = ('com_id', 'group_id', 'teach_id',)


@admin.register(temp_com_teach_info)
class temp_com_teach_info_Admin(admin.ModelAdmin):
	list_display = ('temp_id', 'teach_id',)


@admin.register(teach_inform)
class teach_inform_Admin(admin.ModelAdmin):
	list_display = ('Recipient_acc', 'From_acc', 'title', 'content', 'create_time',)
