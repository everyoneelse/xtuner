from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """扩展用户模型"""
    phone = models.CharField('手机号', max_length=11, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField('出生日期', blank=True, null=True)
    gender_choices = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    gender = models.CharField('性别', max_length=1, choices=gender_choices, blank=True)
    address = models.TextField('地址', blank=True)
    is_verified = models.BooleanField('是否已验证', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'auth_user'

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    """用户资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.CharField('公司', max_length=100, blank=True)
    position = models.CharField('职位', max_length=50, blank=True)
    bio = models.TextField('个人简介', blank=True)
    website = models.URLField('个人网站', blank=True)
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f"{self.user.username}的资料"
