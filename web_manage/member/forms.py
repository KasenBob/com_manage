from django import forms
from ckeditor.fields import RichTextFormField, CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingField, RichTextUploadingFormField

class ArticleForm(forms.Form):
    content = RichTextUploadingFormField()