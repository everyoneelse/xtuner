from django.contrib import admin
from django.utils.html import format_html
from .models import (SiteSettings, Banner, Notification, ActivityLog, 
                    FAQ, ContactMessage, EmailTemplate)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('基本信息', {
            'fields': ('site_name', 'site_description', 'site_keywords', 'logo', 'favicon')
        }),
        ('联系信息', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('社交媒体', {
            'fields': ('weibo_url', 'wechat_qr')
        }),
        ('SEO设置', {
            'fields': ('google_analytics', 'baidu_analytics')
        }),
        ('系统设置', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'sort_order', 'start_date', 'end_date', 'created_at')
    list_filter = ('is_active', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle')
    ordering = ('sort_order', '-created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'read_at')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False  # 只读，不允许手动添加

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'sort_order', 'view_count', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('question', 'answer', 'category')
    ordering = ('sort_order', '-created_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_replied', 'created_at')
    list_filter = ('is_replied', 'created_at', 'replied_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    raw_id_fields = ('replied_by',)
    
    fieldsets = (
        ('联系信息', {
            'fields': ('name', 'email', 'phone', 'created_at')
        }),
        ('消息内容', {
            'fields': ('subject', 'message')
        }),
        ('回复信息', {
            'fields': ('is_replied', 'reply_message', 'replied_by', 'replied_at')
        }),
    )

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'subject', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'subject')
    readonly_fields = ('created_at', 'updated_at')
