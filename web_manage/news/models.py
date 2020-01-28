from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.
class news(models.Model):
	title = models.CharField(max_length=225)
	content = RichTextUploadingField()
	author = models.CharField(max_length=50, default='学科委员会')
	created_time = models.DateField(auto_now_add=True)
	last_update_time = models.DateField(auto_now=True)
	new_photo = models.ImageField(upload_to='news', null=True, blank=True)
