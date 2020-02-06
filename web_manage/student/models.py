from django.db import models


# Create your models here.
# 学生基本信息
class stu_basic_info(models.Model):
	stu_number = models.CharField(max_length=25, primary_key=True, default='0')
	stu_name = models.CharField(max_length=25)
	department = models.ForeignKey('all.depart_info', to_field='depart_name', on_delete=models.SET_NULL, null=True,
	                               blank=True)
	major = models.ForeignKey('all.major_info', to_field='major_name', on_delete=models.SET_NULL, null=True, blank=True)
	grade = models.ForeignKey('all.grade_info', to_field='grade_name', on_delete=models.SET_NULL, null=True, blank=True)
	stu_class = models.ForeignKey('all.class_info', to_field='class_name', on_delete=models.SET_NULL, null=True,
	                              blank=True)
	sex = models.CharField(max_length=10, choices=(("男", "男"), ("女", "女")))
	ID_number = models.CharField(max_length=25, null=True, blank=True)
	bank_number = models.CharField(max_length=25, null=True, blank=True)
	phone_number = models.CharField(max_length=25, null=True, blank=True)
	email = models.EmailField(max_length=255, null=True, blank=True)
	photo = models.ImageField(upload_to='photo', null=True, blank=True)
	stu_card_photo = models.ImageField(upload_to='stu_card_photo', null=True, blank=True)


# 学生-修改基本信息
class temp_stu_basic_info(models.Model):
	stu_number = models.ForeignKey('stu_basic_info', to_field='stu_number', on_delete=models.CASCADE, null=True,
	                               blank=True)
	stu_name = models.CharField(max_length=25)
	department = models.ForeignKey('all.depart_info', to_field='depart_name', on_delete=models.SET_NULL, null=True,
	                               blank=True)
	major = models.ForeignKey('all.major_info', to_field='major_name', on_delete=models.SET_NULL, null=True, blank=True)
	grade = models.ForeignKey('all.grade_info', to_field='grade_name', on_delete=models.SET_NULL, null=True, blank=True)
	stu_class = models.ForeignKey('all.class_info', to_field='class_name', on_delete=models.SET_NULL, null=True,
	                              blank=True)
	sex = models.CharField(max_length=10, choices=(("男", "男"), ("女", "女")))
	ID_number = models.CharField(max_length=25)
	created_time = models.DateField(auto_now=True)
	reason = models.CharField(max_length=225, null=True, blank=True)


# 竞赛学生信息
class com_stu_info(models.Model):
	com_id = models.ForeignKey('competition.com_basic_info', to_field='com_id', on_delete=models.CASCADE)
	group_id = models.ForeignKey('competition.com_group_basic_info', to_field='group_id', on_delete=models.CASCADE)
	stu_id = models.ForeignKey('stu_basic_info', to_field='stu_number', on_delete=models.CASCADE)
	is_leader = models.BooleanField(default=0)
	status = models.CharField(max_length=10, choices=(('0', '未确认'), ('1', '已确认')), default='0')


# 报名修改信息-学生
class temp_com_stu_info(models.Model):
	temp_id = models.ForeignKey('competition.temp_com_group_basic_info', to_field='temp_id', on_delete=models.CASCADE)
	stu_id = models.ForeignKey('stu_basic_info', to_field='stu_number', on_delete=models.CASCADE)
	is_leader = models.BooleanField(default=0)


# 关注比赛表
class stu_fllow_com_info(models.Model):
	stu_id = models.ForeignKey('stu_basic_info', to_field='stu_number', on_delete=models.CASCADE)
	com_id = models.ForeignKey('competition.com_basic_info', to_field='com_id', on_delete=models.CASCADE)
	status = models.BooleanField(default=0)


# 学生通知
class stu_inform(models.Model):
	Recipient_acc = models.ForeignKey('all.user_login_info', related_name="Recipient_acc", to_field='account',
	                                  on_delete=models.CASCADE)
	From_acc = models.ForeignKey('all.user_login_info', related_name="From_acc", to_field='account',
	                             on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=225, null=True, blank=True)
	content = models.TextField(max_length=500, null=True, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=10, choices=(('0', '未读'), ('1', '已读')), default='0')

# 比赛结果
class com_stu_award(models.Model):
	id = models.AutoField(primary_key=True)
	group_id = models.ForeignKey('competition.com_group_basic_info', to_field='group_id', on_delete=models.CASCADE)
	created_time = models.DateField(auto_now=True)
	award = models.CharField(max_length=20, default='无奖项')
