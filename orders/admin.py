from django.contrib import admin
from django.utils.html import format_html
from .models import (Order, OrderItem, Payment, Shipping, ShippingTracking, 
                    Cart, Wishlist)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'product_name', 'product_sku', 'unit_price', 'quantity', 'subtotal')
    readonly_fields = ('subtotal',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_method', 'payment_status', 'amount', 'transaction_id', 'paid_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'final_amount', 
                    'shipping_name', 'created_at')
    list_filter = ('status', 'created_at', 'paid_at', 'shipped_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'shipping_name', 'shipping_phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    raw_id_fields = ('user',)
    inlines = [OrderItemInline, PaymentInline]
    
    fieldsets = (
        ('订单信息', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('金额信息', {
            'fields': ('total_amount', 'shipping_fee', 'discount_amount', 'final_amount')
        }),
        ('收货信息', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address', 'shipping_zip_code')
        }),
        ('备注信息', {
            'fields': ('note', 'admin_note')
        }),
        ('时间记录', {
            'fields': ('paid_at', 'shipped_at', 'delivered_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'product_sku', 'unit_price', 'quantity', 'subtotal')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product__name', 'product_name', 'product_sku')
    raw_id_fields = ('order', 'product')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'payment_status', 'amount', 'transaction_id', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'created_at', 'paid_at')
    search_fields = ('order__order_number', 'transaction_id', 'third_party_id')
    raw_id_fields = ('order',)

@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('order', 'shipping_company', 'tracking_number', 'shipping_status', 'shipped_at')
    list_filter = ('shipping_status', 'shipping_company', 'shipped_at', 'delivered_at')
    search_fields = ('order__order_number', 'tracking_number', 'shipping_company')
    raw_id_fields = ('order',)

@admin.register(ShippingTracking)
class ShippingTrackingAdmin(admin.ModelAdmin):
    list_display = ('shipping', 'location', 'description', 'timestamp')
    list_filter = ('timestamp', 'created_at')
    search_fields = ('shipping__order__order_number', 'location', 'description')
    raw_id_fields = ('shipping',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'subtotal', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    raw_id_fields = ('user', 'product')
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = '小计'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
    raw_id_fields = ('user', 'product')
