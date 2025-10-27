from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    """产品分类"""
    name = models.CharField('分类名称', max_length=100)
    description = models.TextField('描述', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name='父分类')
    image = models.ImageField('分类图片', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('是否激活', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class Brand(models.Model):
    """品牌"""
    name = models.CharField('品牌名称', max_length=100)
    logo = models.ImageField('品牌LOGO', upload_to='brands/', blank=True, null=True)
    description = models.TextField('品牌描述', blank=True)
    website = models.URLField('官方网站', blank=True)
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '品牌'
        verbose_name_plural = '品牌'

    def __str__(self):
        return self.name

class Product(models.Model):
    """产品"""
    name = models.CharField('产品名称', max_length=200)
    slug = models.SlugField('URL别名', unique=True)
    description = models.TextField('产品描述')
    short_description = models.TextField('简短描述', max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='品牌', 
                             blank=True, null=True)
    sku = models.CharField('SKU', max_length=50, unique=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2, 
                                   blank=True, null=True)
    stock_quantity = models.IntegerField('库存数量', default=0)
    min_stock_level = models.IntegerField('最低库存', default=10)
    weight = models.DecimalField('重量(kg)', max_digits=8, decimal_places=3, 
                               blank=True, null=True)
    dimensions = models.CharField('尺寸', max_length=100, blank=True)
    is_active = models.BooleanField('是否上架', default=True)
    is_featured = models.BooleanField('是否推荐', default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level

class ProductImage(models.Model):
    """产品图片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='images', verbose_name='产品')
    image = models.ImageField('图片', upload_to='products/')
    alt_text = models.CharField('替代文本', max_length=200, blank=True)
    is_primary = models.BooleanField('是否为主图', default=False)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '产品图片'
        verbose_name_plural = '产品图片'
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - 图片"

class ProductAttribute(models.Model):
    """产品属性"""
    name = models.CharField('属性名称', max_length=100)
    display_name = models.CharField('显示名称', max_length=100)
    attribute_type_choices = [
        ('text', '文本'),
        ('number', '数字'),
        ('select', '选择'),
        ('color', '颜色'),
        ('size', '尺寸'),
    ]
    attribute_type = models.CharField('属性类型', max_length=20, 
                                    choices=attribute_type_choices, default='text')
    is_required = models.BooleanField('是否必填', default=False)
    is_filterable = models.BooleanField('是否可筛选', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '产品属性'
        verbose_name_plural = '产品属性'

    def __str__(self):
        return self.display_name

class ProductAttributeValue(models.Model):
    """产品属性值"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='attributes', verbose_name='产品')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE,
                                 verbose_name='属性')
    value = models.TextField('属性值')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '产品属性值'
        verbose_name_plural = '产品属性值'
        unique_together = ['product', 'attribute']

    def __str__(self):
        return f"{self.product.name} - {self.attribute.display_name}: {self.value}"
