from django.core.management.base import BaseCommand
from store.models import Tag, Product, TagCategory

class Command(BaseCommand):
    help = 'Создает стандартные теги для татарских товаров'
    
    def handle(self, *args, **kwargs):
        # Сначала создаем категории тегов
        categories_data = [
            {'name': 'fabric', 'order': 1, 'display': 'Ткани'},
            {'name': 'color', 'order': 2, 'display': 'Цвет'},
            {'name': 'event', 'order': 3, 'display': 'Событие'},
            {'name': 'product', 'order': 4, 'display': 'Изделие'},
            {'name': 'style', 'order': 5, 'display': 'Стиль'},
            {'name': 'ornament', 'order': 6, 'display': 'Орнамент'},
        ]
        
        for cat_data in categories_data:
            cat, created = TagCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'order': cat_data['order']}
            )
            if created:
                self.stdout.write(f"✅ Создана категория: {cat_data['display']}")
        
        # Создаем теги с категориями
        tags_data = [
            # События (event)
            {'name': 'сабантуй', 'category': 'event'},
            {'name': 'свадьба', 'category': 'event'},
            {'name': 'повседневный', 'category': 'event'},
            {'name': 'праздничный', 'category': 'event'},
            {'name': 'театр', 'category': 'event'},
            
            # Цвета (color)
            {'name': 'красный', 'category': 'color'},
            {'name': 'синий', 'category': 'color'},
            {'name': 'зеленый', 'category': 'color'},
            {'name': 'розовый', 'category': 'color'},
            {'name': 'золотой', 'category': 'color'},
            {'name': 'серебряный', 'category': 'color'},
            {'name': 'черный', 'category': 'color'},
            {'name': 'белый', 'category': 'color'},
            
            # Типы товаров (product)
            {'name': 'серьги', 'category': 'product'},
            {'name': 'колье', 'category': 'product'},
            {'name': 'платье', 'category': 'product'},
            {'name': 'тюбетейка', 'category': 'product'},
            {'name': 'калфак', 'category': 'product'},
            {'name': 'футболка', 'category': 'product'},
            {'name': 'изю', 'category': 'product'},
            {'name': 'докер', 'category': 'product'},
            
            # Материалы (fabric)
            {'name': 'золото', 'category': 'fabric'},
            {'name': 'серебро', 'category': 'fabric'},
            {'name': 'бархат', 'category': 'fabric'},
            {'name': 'латунь', 'category': 'fabric'},
            {'name': 'хлопок', 'category': 'fabric'},
            {'name': 'итальянская шерсть', 'category': 'fabric'},
            
            # Стили (style)
            {'name': 'татарский стиль', 'category': 'style'},
            {'name': 'национальный', 'category': 'style'},
            {'name': 'традиционный', 'category': 'style'},
            {'name': 'современный', 'category': 'style'},
            
            # Орнаменты (ornament)
            {'name': 'растительный орнамент', 'category': 'ornament'},
            {'name': 'геометрический орнамент', 'category': 'ornament'},
            {'name': 'цветочный узор', 'category': 'ornament'},
        ]
        
        created_count = 0
        
        for tag_data in tags_data:
            category = TagCategory.objects.get(name=tag_data['category'])
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'category': category}
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Создан тег: {tag_data['name']} ({category.get_name_display()})")
            else:
                self.stdout.write(f"ℹ️ Тег уже существует: {tag_data['name']}")
        
        self.stdout.write(self.style.SUCCESS(f'\nСоздано {created_count} тегов'))
        
        # Показываем статистику
        self.stdout.write("\n Статистика:")
        self.stdout.write(f"Всего тегов в базе: {Tag.objects.count()}")
        self.stdout.write(f"Всего товаров: {Product.objects.count()}")