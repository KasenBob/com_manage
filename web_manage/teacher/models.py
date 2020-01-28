from django.db import models


# Create your models here.
# 职称信息
class profess_info(models.Model):
	profess_name = models.CharField(max_length=10, primary_key=True)


# 指导教师基本信息
class teach_basic_info(models.Model):
	tea_number = models.CharField(max_length=25, primary_key=True, default='0')
	tea_name = models.CharField(max_length=25)
	profess = models.ForeignKey('profess_info', to_field='profess_name', on_delete=models.SET_NULL, null=True,
	                            blank=True)
	department = models.ForeignKey('all.depart_info', to_field='depart_name', on_delete=models.SET_NULL, null=True,
	                               blank=True)
	part = models.CharField(max_length=25, null=True, blank=True)
	ID_number = models.CharField(max_length=25, null=True, blank=True)
	email = models.EmailField(max_length=255, null=True, blank=True)
	phone_number = models.CharField(max_length=25, null=True, blank=True)
	photo = models.ImageField(upload_to='photo', null=True, blank=True)



# 申请修改个人信息
class temp_teach_basic_info(models.Model):
	teach_number = models.ForeignKey('teach_basic_info', to_field='tea_number', on_delete=models.CASCADE, null=True,
	                                 blank=True)
	tea_name = models.CharField(max_length=25)
	profess = models.ForeignKey('profess_info', to_field='profess_name', on_delete=models.SET_NULL, null=True,
	                            blank=True)
	department = models.ForeignKey('all.depart_info', to_field='depart_name', on_delete=models.SET_NULL, null=True,
	                               blank=True)
	created_time = models.DateField(auto_now=True)


# 竞赛指导老师信息
class com_teach_info(models.Model):
	com_id = models.ForeignKey('competition.com_basic_info', to_field='com_id', on_delete=models.CASCADE)
	group_id = models.ForeignKey('competition.com_group_basic_info', to_field='group_id', on_delete=models.CASCADE)
	teach_id = models.ForeignKey('teach_basic_info', to_field='tea_number', on_delete=models.CASCADE)
	status = models.CharField(max_length=10, choices=(('0', '未确认'), ('1', '已确认')), default='0')


# 报名修改信息-教师
class temp_com_teach_info(models.Model):
	temp_id = models.ForeignKey('competition.temp_com_group_basic_info', to_field='temp_id', on_delete=models.CASCADE)
	teach_id = models.ForeignKey('teach_basic_info', to_field='tea_number', on_delete=models.CASCADE)


# 教师通知
class teach_inform(models.Model):
	Recipient_acc = models.ForeignKey('all.user_login_info', related_name="Recipient", to_field='account',
	                                  on_delete=models.CASCADE)
	From_acc = models.ForeignKey('all.user_login_info', related_name="From", to_field='account',
	                             on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=225, null=True, blank=True)
	content = models.TextField(max_length=500, null=True, blank=True)
	create_time = models.DateTimeField(auto_now=True)
