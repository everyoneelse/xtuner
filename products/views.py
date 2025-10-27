from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from django.http import JsonResponse
from core.models import SiteSettings
from .models import Product, Category, Brand, ProductAttribute

def get_site_settings():
    """获取网站设置"""
    try:
        return SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        return None

def product_list(request):
    """产品列表"""
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    # 筛选条件
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search', '').strip()
    sort = request.GET.get('sort', 'created_at')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    # 排序
    sort_options = {
        'created_at': '-created_at',
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price',
    }
    if sort in sort_options:
        products = products.order_by(sort_options[sort])
    
    # 分页
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取筛选选项
    categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
    brands = Brand.objects.filter(is_active=True).order_by('name')
    
    # 价格范围
    price_range = Product.objects.filter(is_active=True).aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        'site_settings': get_site_settings(),
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'price_range': price_range,
        'current_category': int(category_id) if category_id else None,
        'current_brand': int(brand_id) if brand_id else None,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'search_query': search,
        'current_sort': sort,
        'total_products': products.count(),
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    """产品详情"""
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand', 'created_by')
        .prefetch_related('images', 'attributes__attribute'),
        slug=slug,
        is_active=True
    )
    
    # 相关产品
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category', 'brand')[:4]
    
    context = {
        'site_settings': get_site_settings(),
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def category_list(request):
    """分类列表"""
    categories = Category.objects.filter(
        is_active=True, 
        parent=None
    ).prefetch_related('children').order_by('sort_order', 'name')
    
    context = {
        'site_settings': get_site_settings(),
        'categories': categories,
    }
    return render(request, 'products/category_list.html', context)

def category_detail(request, pk):
    """分类详情"""
    category = get_object_or_404(Category, pk=pk, is_active=True)
    
    # 获取该分类及其子分类的所有产品
    category_ids = [category.id]
    if category.children.exists():
        category_ids.extend(category.children.filter(is_active=True).values_list('id', flat=True))
    
    products = Product.objects.filter(
        category_id__in=category_ids,
        is_active=True
    ).select_related('category', 'brand')
    
    # 筛选和排序
    brand_id = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', 'created_at')
    
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # 排序
    sort_options = {
        'created_at': '-created_at',
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price',
    }
    if sort in sort_options:
        products = products.order_by(sort_options[sort])
    
    # 分页
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取该分类下的品牌
    brands = Brand.objects.filter(
        product__category_id__in=category_ids,
        is_active=True
    ).distinct().order_by('name')
    
    # 价格范围
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        'site_settings': get_site_settings(),
        'category': category,
        'page_obj': page_obj,
        'brands': brands,
        'price_range': price_range,
        'current_brand': int(brand_id) if brand_id else None,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_sort': sort,
        'total_products': products.count(),
    }
    return render(request, 'products/category_detail.html', context)

def brand_list(request):
    """品牌列表"""
    brands = Brand.objects.filter(is_active=True).order_by('name')
    
    paginator = Paginator(brands, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'site_settings': get_site_settings(),
        'page_obj': page_obj,
    }
    return render(request, 'products/brand_list.html', context)

def brand_detail(request, pk):
    """品牌详情"""
    brand = get_object_or_404(Brand, pk=pk, is_active=True)
    
    products = Product.objects.filter(
        brand=brand,
        is_active=True
    ).select_related('category', 'brand')
    
    # 筛选和排序
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', 'created_at')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # 排序
    sort_options = {
        'created_at': '-created_at',
        'name': 'name',
        'price_asc': 'price',
        'price_desc': '-price',
    }
    if sort in sort_options:
        products = products.order_by(sort_options[sort])
    
    # 分页
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取该品牌下的分类
    categories = Category.objects.filter(
        product__brand=brand,
        is_active=True
    ).distinct().order_by('sort_order', 'name')
    
    # 价格范围
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        'site_settings': get_site_settings(),
        'brand': brand,
        'page_obj': page_obj,
        'categories': categories,
        'price_range': price_range,
        'current_category': int(category_id) if category_id else None,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_sort': sort,
        'total_products': products.count(),
    }
    return render(request, 'products/brand_detail.html', context)
