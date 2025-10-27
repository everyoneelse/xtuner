from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Brand, Product, ProductImage, 
                    ProductAttribute, ProductAttributeValue)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    fields = ('attribute', 'value')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {}
    ordering = ('sort_order', 'name')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 
                    'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category', 'brand', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('created_by',)
    inlines = [ProductImageInline, ProductAttributeValueInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'created_by')
        }),
        ('描述信息', {
            'fields': ('description', 'short_description')
        }),
        ('价格库存', {
            'fields': ('price', 'cost_price', 'stock_quantity', 'min_stock_level')
        }),
        ('规格信息', {
            'fields': ('weight', 'dimensions')
        }),
        ('状态设置', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand', 'created_by')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_primary', 'sort_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    raw_id_fields = ('product',)

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'attribute_type', 'is_required', 'is_filterable')
    list_filter = ('attribute_type', 'is_required', 'is_filterable')
    search_fields = ('name', 'display_name')

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value', 'created_at')
    list_filter = ('attribute', 'created_at')
    search_fields = ('product__name', 'attribute__display_name', 'value')
    raw_id_fields = ('product', 'attribute')
