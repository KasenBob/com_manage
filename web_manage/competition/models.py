from django.db import models
from datetime import datetime
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.
# 系列比赛信息
class series_info(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50, unique=True)
	introduction = models.TextField(null=True, blank=True)
	photo = models.ImageField(upload_to='series_photo', null=True, blank=True)
	type = models.CharField(max_length=10, choices=(('0', '个人赛'), ('1', '团体赛')), default='0')
	now_com_id = models.ForeignKey('com_basic_info', to_field='com_id', on_delete=models.SET_NULL, null=True,
	                               blank=True)
	status = models.CharField(max_length=5, choices=(('0', '显示'), ('1', '隐藏')), default='0')

	def update_com_id(self):
		com_list = com_basic_info.objects.filter(series_id=self.id).order_by('-begin_regit')
		flag = 1
		for new_com in com_list:
			if flag == 1:
				self.now_com_id = new_com
				flag = 0
			else:
				break
		self.save()


# 系列针对院系
class series_depart(models.Model):
	id = models.AutoField(primary_key=True)
	series_id = models.ForeignKey('series_info', to_field='id', on_delete=models.CASCADE)
	depart_name = models.ForeignKey('all.depart_info', to_field='depart_name', on_delete=models.CASCADE)


# 竞赛基本信息
class com_basic_info(models.Model):
	com_id = models.AutoField(primary_key=True)
	com_name = models.CharField(max_length=50, unique=True)
	series_id = models.ForeignKey('series_info', to_field='id', on_delete=models.SET_NULL, null=True, blank=True)
	type = models.CharField(max_length=10, choices=(('0', '个人赛'), ('1', '团体赛')), default='0')
	begin_regit = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	end_regit = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	begin_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	end_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	num_stu = models.IntegerField(default=1)
	need_full = models.BooleanField(default=0)
	same_stu = models.BooleanField(default=0)
	com_sort_num = models.IntegerField(default=0)
	com_web = models.CharField(max_length=225, null=True, blank=True)
	if_web = models.IntegerField(default=0)
	num_teach = models.IntegerField(default=1)
	com_status = models.CharField(max_length=10, choices=(('0', '报名中'), ('1', '报名结束'), ('2', '比赛中'), ('3', '比赛结束')),
	                              default='0')

	def update_status(self):
		now_time = datetime.now()
		if now_time >= self.begin_regit and now_time < self.end_regit:
			self.com_status = '0'
		elif now_time >= self.end_regit and now_time < self.begin_time:
			self.com_status = '1'
		elif now_time >= self.begin_time and now_time < self.end_time:
			self.com_status = '2'
		else:
			self.com_status = '3'
		self.save()


# 竞赛组别信息
class com_sort_info(models.Model):
	id = models.AutoField(primary_key=True)
	com_id = models.ForeignKey('com_basic_info', to_field='com_id', on_delete=models.CASCADE)
	sort_name = models.CharField(max_length=50)


# 竞赛小组信息
class com_group_basic_info(models.Model):
	group_id = models.AutoField(primary_key=True)
	com_id = models.ForeignKey('com_basic_info', to_field='com_id', on_delete=models.SET_NULL, null=True, blank=True)
	group_name = models.CharField(max_length=25, null=True, blank=True)
	group_num = models.IntegerField(default=1)
	com_group = models.ForeignKey('com_sort_info', to_field='id', on_delete=models.SET_NULL, null=True, blank=True)
	product_name = models.CharField(max_length=50, null=True, blank=True)
	else_info = models.TextField(default='', null=True, blank=True)
	apply_time = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=10, choices=(('0', '未成功'), ('1', '已成功')), default='0')


# 竞赛报名表所需信息信息
class com_need_info(models.Model):
	com_id = models.IntegerField(primary_key=True)
	stu_num = models.BooleanField(default=0)
	stu_name = models.BooleanField(default=0)
	ID_number = models.BooleanField(default=0)
	sex = models.BooleanField(default=0)
	depart = models.BooleanField(default=0)
	major = models.BooleanField(default=0)
	grade = models.BooleanField(default=0)
	stu_class = models.BooleanField(default=0)
	email = models.BooleanField(default=0)
	phone_num = models.BooleanField(default=0)
	com_group = models.BooleanField(default=0)
	group_name = models.BooleanField(default=0)
	product_name = models.BooleanField(default=0)
	tea_num = models.IntegerField(default=0)
	bank_number = models.BooleanField(default=0)
	else_info = models.BooleanField(default=0)


# 学生申请修改报名信息
class temp_com_group_basic_info(models.Model):
	temp_id = models.AutoField(primary_key=True)
	group_id = models.ForeignKey('com_group_basic_info', to_field='group_id', on_delete=models.CASCADE,
	                             default='')
	com_id = models.ForeignKey('com_basic_info', to_field='com_id', on_delete=models.CASCADE, default='')
	group_name = models.CharField(max_length=25, null=True, blank=True)
	group_num = models.IntegerField(default=1)
	com_group = models.ForeignKey('com_sort_info', to_field='id', on_delete=models.SET_NULL, null=True,
	                              blank=True)
	product_name = models.CharField(max_length=50, null=True, blank=True)
	else_info = models.TextField(default='', null=True, blank=True)
	created_time = models.DateField(auto_now=True)
	apply_type = models.CharField(max_length=5, choices=(('1', '修改信息'), ('2', '撤销报名')), default='1')
