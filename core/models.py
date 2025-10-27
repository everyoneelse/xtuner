from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class SiteSettings(models.Model):
    """网站设置"""
    site_name = models.CharField('网站名称', max_length=100, default='我的网站')
    site_description = models.TextField('网站描述', blank=True)
    site_keywords = models.TextField('网站关键词', blank=True)
    logo = models.ImageField('网站LOGO', upload_to='site/', blank=True, null=True)
    favicon = models.ImageField('网站图标', upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField('联系邮箱', blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    address = models.TextField('地址', blank=True)
    
    # 社交媒体链接
    weibo_url = models.URLField('微博链接', blank=True)
    wechat_qr = models.ImageField('微信二维码', upload_to='site/', blank=True, null=True)
    
    # SEO设置
    google_analytics = models.TextField('Google Analytics代码', blank=True)
    baidu_analytics = models.TextField('百度统计代码', blank=True)
    
    # 系统设置
    maintenance_mode = models.BooleanField('维护模式', default=False)
    maintenance_message = models.TextField('维护提示信息', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # 确保只有一个设置实例
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('只能有一个网站设置实例')
        return super().save(*args, **kwargs)

class Banner(models.Model):
    """轮播图"""
    title = models.CharField('标题', max_length=200)
    subtitle = models.CharField('副标题', max_length=200, blank=True)
    image = models.ImageField('图片', upload_to='banners/')
    link = models.URLField('链接', blank=True)
    button_text = models.CharField('按钮文字', max_length=50, blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    sort_order = models.IntegerField('排序', default=0)
    start_date = models.DateTimeField('开始时间', null=True, blank=True)
    end_date = models.DateTimeField('结束时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_valid(self):
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return self.is_active

class Notification(models.Model):
    """通知"""
    NOTIFICATION_TYPE_CHOICES = [
        ('info', '信息'),
        ('success', '成功'),
        ('warning', '警告'),
        ('error', '错误'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name='用户', related_name='notifications')
    title = models.CharField('标题', max_length=200)
    message = models.TextField('消息内容')
    notification_type = models.CharField('通知类型', max_length=20, 
                                       choices=NOTIFICATION_TYPE_CHOICES, default='info')
    is_read = models.BooleanField('是否已读', default=False)
    link = models.URLField('相关链接', blank=True)
    
    # 关联对象（可选）
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                   null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class ActivityLog(models.Model):
    """活动日志"""
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
        ('view', '查看'),
        ('download', '下载'),
        ('upload', '上传'),
        ('other', '其他'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name='用户', null=True, blank=True,
                            related_name='activity_logs')
    action = models.CharField('操作', max_length=20, choices=ACTION_CHOICES)
    description = models.TextField('描述')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    
    # 关联对象
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                   null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 额外数据
    extra_data = models.JSONField('额外数据', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '活动日志'
        verbose_name_plural = '活动日志'
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else '匿名用户'
        return f"{user_str} - {self.get_action_display()}: {self.description}"

class FAQ(models.Model):
    """常见问题"""
    question = models.CharField('问题', max_length=300)
    answer = models.TextField('答案')
    category = models.CharField('分类', max_length=100, blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    sort_order = models.IntegerField('排序', default=0)
    view_count = models.IntegerField('查看次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '常见问题'
        verbose_name_plural = '常见问题'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.question

class ContactMessage(models.Model):
    """联系消息"""
    name = models.CharField('姓名', max_length=100)
    email = models.EmailField('邮箱')
    phone = models.CharField('电话', max_length=20, blank=True)
    subject = models.CharField('主题', max_length=200)
    message = models.TextField('消息内容')
    is_replied = models.BooleanField('是否已回复', default=False)
    reply_message = models.TextField('回复内容', blank=True)
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                  null=True, blank=True, verbose_name='回复人',
                                  related_name='replied_messages')
    replied_at = models.DateTimeField('回复时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '联系消息'
        verbose_name_plural = '联系消息'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class EmailTemplate(models.Model):
    """邮件模板"""
    name = models.CharField('模板名称', max_length=100)
    code = models.CharField('模板代码', max_length=50, unique=True)
    subject = models.CharField('邮件主题', max_length=200)
    html_content = models.TextField('HTML内容')
    text_content = models.TextField('文本内容', blank=True)
    variables = models.JSONField('可用变量', blank=True, null=True, 
                                help_text='JSON格式的变量说明')
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '邮件模板'
        verbose_name_plural = '邮件模板'

    def __str__(self):
        return self.name
