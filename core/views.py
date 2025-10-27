from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import SiteSettings, Banner, FAQ, ContactMessage, Notification
from products.models import Product, Category
from orders.models import Order

def get_site_settings():
    """获取网站设置"""
    try:
        return SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        return None

def home(request):
    """首页"""
    context = {
        'site_settings': get_site_settings(),
        'banners': Banner.objects.filter(is_active=True).order_by('sort_order'),
        'featured_products': Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category', 'brand')[:8],
        'categories': Category.objects.filter(is_active=True, parent=None).order_by('sort_order')[:6],
    }
    return render(request, 'core/home.html', context)

def about(request):
    """关于我们"""
    context = {
        'site_settings': get_site_settings(),
    }
    return render(request, 'core/about.html', context)

def contact(request):
    """联系我们"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, '您的消息已发送成功，我们会尽快回复您！')
            return redirect('core:contact')
        else:
            messages.error(request, '请填写所有必填字段。')
    
    context = {
        'site_settings': get_site_settings(),
    }
    return render(request, 'core/contact.html', context)

def faq_list(request):
    """常见问题列表"""
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    faqs = FAQ.objects.filter(is_active=True)
    
    if category:
        faqs = faqs.filter(category=category)
    
    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) | Q(answer__icontains=search)
        )
    
    categories = FAQ.objects.filter(is_active=True).values_list(
        'category', flat=True
    ).distinct().exclude(category='')
    
    paginator = Paginator(faqs.order_by('sort_order', '-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'site_settings': get_site_settings(),
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'search_query': search,
    }
    return render(request, 'core/faq_list.html', context)

def faq_detail(request, pk):
    """常见问题详情"""
    faq = get_object_or_404(FAQ, pk=pk, is_active=True)
    
    # 增加查看次数
    FAQ.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    
    context = {
        'site_settings': get_site_settings(),
        'faq': faq,
    }
    return render(request, 'core/faq_detail.html', context)

@login_required
def dashboard(request):
    """用户仪表板"""
    user = request.user
    
    # 获取用户的订单统计
    orders = Order.objects.filter(user=user)
    order_stats = {
        'total': orders.count(),
        'pending': orders.filter(status='pending').count(),
        'paid': orders.filter(status='paid').count(),
        'shipped': orders.filter(status='shipped').count(),
        'delivered': orders.filter(status='delivered').count(),
    }
    
    # 最近的订单
    recent_orders = orders.order_by('-created_at')[:5]
    
    # 未读通知
    unread_notifications = user.notifications.filter(is_read=False).count()
    
    context = {
        'site_settings': get_site_settings(),
        'order_stats': order_stats,
        'recent_orders': recent_orders,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def notifications(request):
    """用户通知列表"""
    notifications = request.user.notifications.order_by('-created_at')
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'site_settings': get_site_settings(),
        'page_obj': page_obj,
    }
    return render(request, 'core/notifications.html', context)

@login_required
def mark_notification_read(request, pk):
    """标记通知为已读"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('core:notifications')

@login_required
def mark_all_notifications_read(request):
    """标记所有通知为已读"""
    request.user.notifications.filter(is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('core:notifications')

def search(request):
    """全站搜索"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('core:home')
    
    # 搜索产品
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(short_description__icontains=query),
        is_active=True
    ).select_related('category', 'brand')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'site_settings': get_site_settings(),
        'page_obj': page_obj,
        'query': query,
        'total_results': products.count(),
    }
    return render(request, 'core/search_results.html', context)
