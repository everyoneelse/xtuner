from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product

class Order(models.Model):
    """订单"""
    ORDER_STATUS_CHOICES = [
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('processing', '处理中'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    order_number = models.CharField('订单号', max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name='用户', related_name='orders')
    status = models.CharField('订单状态', max_length=20, choices=ORDER_STATUS_CHOICES,
                             default='pending')
    total_amount = models.DecimalField('总金额', max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField('运费', max_digits=8, decimal_places=2, default=0)
    discount_amount = models.DecimalField('优惠金额', max_digits=8, decimal_places=2, default=0)
    final_amount = models.DecimalField('实付金额', max_digits=10, decimal_places=2)
    
    # 收货信息
    shipping_name = models.CharField('收货人姓名', max_length=100)
    shipping_phone = models.CharField('收货人电话', max_length=20)
    shipping_address = models.TextField('收货地址')
    shipping_zip_code = models.CharField('邮政编码', max_length=10, blank=True)
    
    # 备注信息
    note = models.TextField('订单备注', blank=True)
    admin_note = models.TextField('管理员备注', blank=True)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    paid_at = models.DateTimeField('付款时间', null=True, blank=True)
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    delivered_at = models.DateTimeField('送达时间', null=True, blank=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"订单 {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # 生成订单号
            import uuid
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """订单项"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='产品')
    product_name = models.CharField('产品名称', max_length=200)  # 冗余存储，防止产品删除
    product_sku = models.CharField('产品SKU', max_length=50)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    quantity = models.IntegerField('数量')
    subtotal = models.DecimalField('小计', max_digits=10, decimal_places=2)
    
    # 产品属性快照
    product_attributes = models.JSONField('产品属性', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '订单项'
        verbose_name_plural = '订单项'

    def __str__(self):
        return f"{self.order.order_number} - {self.product_name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

class Payment(models.Model):
    """支付记录"""
    PAYMENT_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('bank_card', '银行卡'),
        ('cash', '现金'),
        ('other', '其他'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='payments', verbose_name='订单')
    payment_method = models.CharField('支付方式', max_length=20, 
                                    choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField('支付状态', max_length=20,
                                    choices=PAYMENT_STATUS_CHOICES, default='pending')
    amount = models.DecimalField('支付金额', max_digits=10, decimal_places=2)
    transaction_id = models.CharField('交易流水号', max_length=100, blank=True)
    third_party_id = models.CharField('第三方交易号', max_length=100, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)

    class Meta:
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_payment_method_display()}"

class Shipping(models.Model):
    """配送记录"""
    SHIPPING_STATUS_CHOICES = [
        ('preparing', '准备中'),
        ('shipped', '已发货'),
        ('in_transit', '运输中'),
        ('delivered', '已送达'),
        ('returned', '已退回'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, 
                                related_name='shipping', verbose_name='订单')
    shipping_company = models.CharField('快递公司', max_length=100, blank=True)
    tracking_number = models.CharField('快递单号', max_length=100, blank=True)
    shipping_status = models.CharField('配送状态', max_length=20,
                                     choices=SHIPPING_STATUS_CHOICES, default='preparing')
    
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    delivered_at = models.DateTimeField('送达时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '配送记录'
        verbose_name_plural = '配送记录'

    def __str__(self):
        return f"{self.order.order_number} - 配送"

class ShippingTracking(models.Model):
    """配送跟踪"""
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE,
                               related_name='tracking_records', verbose_name='配送')
    location = models.CharField('位置', max_length=200)
    description = models.TextField('描述')
    timestamp = models.DateTimeField('时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '配送跟踪'
        verbose_name_plural = '配送跟踪'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.shipping.order.order_number} - {self.location}"

class Cart(models.Model):
    """购物车"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name='用户', related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='产品')
    quantity = models.IntegerField('数量', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Wishlist(models.Model):
    """收藏夹"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name='用户', related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='产品')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏夹'
        verbose_name_plural = '收藏夹'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
