from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from decimal import Decimal


class Profile(models.Model):
    class Meta:
        verbose_name_plural = 'Профиль'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username

def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

post_save.connect(create_profile, sender=User)

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Категории'

class Customer(models.Model):
    class Meta:
        verbose_name_plural = 'Клиенты'
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Brand(models.Model):
    class Meta:
        verbose_name_plural = 'Бренды'
        ordering = ['brand_name']  # Сортировка по алфавиту
        
    brand_name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.brand_name


class Product(models.Model):
    class Meta:
        verbose_name_plural = 'Товары'
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=8)
    categories = models.ManyToManyField(Category, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')  
    description = models.CharField(max_length=500, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=8)
    COLOR_CHOICES = [
        ('red', 'Красный'),
        ('blue', 'Синий'),
        ('green', 'Зеленый'),
        ('yellow', 'Желтый'),
        ('white', 'Белый'),
        ('black', 'Черный'),
        ('pink', 'Розовый'),
        ('purple', 'Фиолетовый'),
        ('orange', 'Оранжевый'),
        ('brown', 'Коричневый'),
        ('gold', 'Золотой'),
        ('silver', 'Серебряный'),
        ('multi', 'Многоцветный'),
    ]
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        blank=True,
        null=True,
        verbose_name='Основной цвет'
    )
    
    material = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Материал (например: золото, хлопок, дерево)'
    )
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Теги')
    
    def get_info_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': str(self.price),
            'color': self.get_color_display() if self.color else 'Не указан',
            'category': self.category.name if self.category else 'Без категории',
            'image_url': self.image.url if self.image else '',
        }

    def __str__(self):
        return self.name


class TagCategory(models.Model):
    CATEGORY_CHOICES = [
        ('fabric', 'Материал'),
        ('color', 'Цвет'), 
        ('event', 'Событие'),
        ('product', 'Изделие'),
        ('style', 'Стиль'),
        ('ornament', 'Орнамент'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        unique=True,
        verbose_name='Название категории'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Категория тегов'
        verbose_name_plural = 'Категории тегов'
           
    def __str__(self):
        return self.get_name_display()
    
class Tag(models.Model):
    """Теги с категориями"""
    name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Название тега',
        help_text='Например: сабантуй, красный, бархат, серьги'
    )
    
    category = models.ForeignKey(
        TagCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tags',
        verbose_name='Категория тега',
        help_text='Выберите категорию тега'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-created_at']  
    
    def __str__(self):
        category_name = self.category.get_name_display() if self.category else 'Без категории'
        return f"{category_name}: {self.name}"
    
    def get_products_count(self):
        return self.product_set.count()
    get_products_count.short_description = 'Количество товаров'


class Order(models.Model):
    class Meta:
        verbose_name_plural = 'Заказы'
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product



class HistoricalArticle(models.Model):
    """Исторические статьи о татарской культуре"""
    
    ARTICLE_TYPES = [
        ('costume', 'Татарский костюм'),
        ('headwear', 'Головные уборы'),
        ('jewelry', 'Украшения'),
        ('ornament', 'Орнаменты и узоры'),
        ('craft', 'Ремесла и техники'),
        ('holiday', 'Праздники и традиции'),
    ]
    
    # Основная информация
    title = models.CharField(max_length=200, verbose_name='Название статьи')
    article_type = models.CharField(max_length=50, choices=ARTICLE_TYPES)
    
    # Контент
    short_description = models.TextField(verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Текст статьи')
    
    # Изображение
    main_image = models.ImageField(upload_to='articles/', verbose_name='Изображение')
    
    # Связь с товарами
    related_products = models.ManyToManyField(
        Product, 
        blank=True,
        verbose_name='Связанные товары'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Историческая статья'
        verbose_name_plural = 'Исторические статьи'
        ordering = ['-created_at']  
    
    def __str__(self):
        return self.title

class ChatHistory(models.Model):
    """История чата с AI-стилистом для каждого пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_histories')
    message = models.TextField(verbose_name='Сообщение')
    response = models.TextField(verbose_name='Ответ стилиста')
    products_data = models.JSONField(default=list, blank=True, verbose_name='Предложенные товары')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'История чата'
        verbose_name_plural = 'Истории чатов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Чат {self.user.username} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'