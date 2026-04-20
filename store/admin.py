from django.contrib import admin
from .models import (
    Category, Customer, Product, Order, Profile, Brand, 
    Tag, TagCategory, HistoricalArticle
)
from django.contrib.auth.models import User
from django.utils.html import format_html


# Инфа о пользователе
class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username", 'first_name', "last_name", "email"]
    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(TagCategory)
class TagCategoryAdmin(admin.ModelAdmin):
    """Админка для управления категориями тегов"""
    
    list_display = ['name_display', 'tags_count']  
    search_fields = ['name']
    list_filter = ['name']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name']  
        }),
    ]
    
    def name_display(self, obj):
        """Отображение названия категории с выбором"""
        return obj.get_name_display()
    name_display.short_description = 'Категория'
    
    def tags_count(self, obj):
        """Количество тегов в категории"""
        count = obj.tags.count()
        return format_html(
            '<a href="/admin/store/tag/?category__id__exact={}" style="color: #2c7a51; font-weight: bold;">{} тег(ов)</a>',
            obj.id, count
        )
    tags_count.short_description = 'Теги'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для управления тегами"""
    
    list_display = ['name', 'category', 'products_count', 'created_at']
    search_fields = ['name', 'category__name']
    list_filter = ['category', 'created_at']
    list_per_page = 20
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'category']
        }),
        ('Дополнительно', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    actions = ['duplicate_tag']
    
    def products_count(self, obj):
        """Количество товаров с тегом"""
        count = obj.product_set.count()
        return format_html(
            '<a href="/admin/store/product/?tags__id__exact={}" style="color: #2c7a51; font-weight: bold;">{} товар(ов)</a>',
            obj.id, count
        )
    products_count.short_description = 'Товары'
    
    def duplicate_tag(self, request, queryset):
        """Дублирование выбранных тегов"""
        for tag in queryset:
            new_tag = Tag.objects.create(
                name=f"{tag.name} (копия)",
                category=tag.category
            )
            self.message_user(request, f'Тег "{tag.name}" скопирован как "{new_tag.name}"')
    duplicate_tag.short_description = "Дублировать теги"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'get_categories', 'brand', 'color_display', 'tags_by_category', 'is_sale']
    search_fields = ['name', 'description', 'tags__name']
    list_filter = ['categories', 'brand', 'color', 'tags', 'is_sale', 'tags__category']
    list_per_page = 20
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'description', 'price', 'categories', 'brand', 'image']
        }),
        ('Цены и скидки', {
            'fields': ['is_sale', 'sale_price']
        }),
        ('Характеристики', {
            'fields': ['color', 'material']
        }),
        ('Теги', {
            'fields': ['tags'],
            'description': 'Теги сгруппированы по категориям в фильтре'
        }),
    ]
    
    filter_horizontal = ['tags', 'categories']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'categories', 'tags', 'tags__category'
        )
    
    actions = ['add_sabantuy_tag', 'add_tatar_style_tag', 'enable_sale', 'disable_sale']
    
    def get_categories(self, obj):
        """Отображение категорий"""
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Категории'
    
    def color_display(self, obj):
        """Отображение цвета"""
        if obj.color:
            return obj.get_color_display()  # Просто возвращаем название цвета
        return "-"
    color_display.short_description = 'Цвет'
    
    def tags_by_category(self, obj):
        """Список тегов, сгруппированные по категориям"""
        tags = obj.tags.all().select_related('category')
        if tags:
            tag_list = []
            for tag in tags:
                cat_name = tag.category.get_name_display() if tag.category else 'Без категории'
                tag_list.append(f"{cat_name}: {tag.name}")
                return ", ".join(tag_list)  
            return "-"
    def add_sabantuy_tag(self, request, queryset):
        """Добавить тег "сабантуй" к выбранным товарам"""
        event_category, _ = TagCategory.objects.get_or_create(
            name='event',
        )
        sabantuy_tag, created = Tag.objects.get_or_create(
            name='сабантуй',
            defaults={'category': event_category}
        )
        for product in queryset:
            product.tags.add(sabantuy_tag)
        self.message_user(request, f'Тег "сабантуй" добавлен к {queryset.count()} товарам')
    add_sabantuy_tag.short_description = "Добавить тег 'сабантуй'"
    
    def add_tatar_style_tag(self, request, queryset):
        """Добавить тег "татарский стиль" к выбранным товарам"""
        style_category, _ = TagCategory.objects.get_or_create(
            name='style',
        )
        tatar_style_tag, created = Tag.objects.get_or_create(
            name='татарский стиль',
            defaults={'category': style_category}
        )
        for product in queryset:
            product.tags.add(tatar_style_tag)
        self.message_user(request, f'Тег "татарский стиль" добавлен к {queryset.count()} товарам')
    add_tatar_style_tag.short_description = "Добавить тег 'татарский стиль'"
    
    def enable_sale(self, request, queryset):
        """Включить скидку для выбранных товаров"""
        queryset.update(is_sale=True)
        self.message_user(request, f'Скидка включена для {queryset.count()} товаров')
    enable_sale.short_description = "Включить скидку"
    
    def disable_sale(self, request, queryset):
        """Выключить скидку для выбранным товарам"""
        queryset.update(is_sale=False)
        self.message_user(request, f'Скидка выключена для {queryset.count()} товаров')
    disable_sale.short_description = "Выключить скидку"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count']
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Товаров'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email']
    search_fields = ['first_name', 'last_name', 'phone', 'email']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'quantity', 'date', 'status']
    list_filter = ['date', 'status']
    search_fields = ['customer__first_name', 'customer__last_name', 'product__name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'product_count']
    search_fields = ['brand_name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Товаров'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'date_modified']
    search_fields = ['user__username', 'phone', 'city']
    list_filter = ['city', 'country']


@admin.register(HistoricalArticle)
class HistoricalArticleAdmin(admin.ModelAdmin):
    
    list_display = ['title', 'article_type', 'created_at'] 
   
    list_filter = ['article_type']
    search_fields = ['title', 'content']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'article_type'] 
        }),
        ('Контент', {
            'fields': ['short_description', 'content'],
            'classes': ['wide']
        }),
        ('Изображение', {
            'fields': ['main_image'],
        }),
        ('Связанные товары', {
            'fields': ['related_products'],
            'classes': ['collapse']
        }),
    ]
    
    filter_horizontal = ['related_products']