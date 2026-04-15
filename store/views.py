from django.shortcuts import render, redirect, get_object_or_404  
from .models import Product, Category, Profile, Brand, HistoricalArticle
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePassword, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import re
import json
from cart.cart import Cart
from django.templatetags.static import static
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import openai
from django.apps import apps
import random


def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        # Поиск по названию и описанию без учета регистра
        products = Product.objects.filter(
            Q(name__icontains=searched) | 
            Q(description__icontains=searched)
        )
        return render(request, 'search.html', {
            'searched': products,
            'searched_query': searched
        })
    else:
        return render(request, 'search.html', {})


def update_info(request):
    if request.user.is_authenticated:
        # Получаем или создаем профиль пользователя
        current_user, created = Profile.objects.get_or_create(user=request.user)
        
        # Получаем или создаем адрес доставки
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if request.method == 'POST':
            if form.is_valid() and shipping_form.is_valid():
                form.save()
                shipping_form.save()
                messages.success(request, "Информация о пользователе обновлена")
                return redirect('home')
        
        return render(request, "update_info.html", {
            'form': form,
            'shipping_form': shipping_form
        })
    else:
        messages.success(request, "Войдите в систему")
        return redirect('home')
      

        
def update_password(request):

        if request.user.is_authenticated:
                current_user = request.user
                if request.method == 'POST':
                        form = ChangePassword(current_user, request.POST)
                        if form.is_valid():
                                form.save()
                                messages.success(request, "Ваш пароль обновлен, пожалуйста, войдите снова")
                                login(request, current_user)
                                return redirect('update_user')
                        else:
                                for error in list(form.errors.values()):
                                        messages.error(request, error)
                                        return redirect ('update_password')
                else:
                        form = ChangePassword(current_user)
                        return render(request, "update_password.html", {'form': form})
        else:
                messages.success(request, "Вы должны войти в систему")
                return redirect('home')


def update_user(request):
    if not request.user.is_authenticated:
        messages.error(request, "Войдите в систему")
        return redirect('home')

    current_user = request.user

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=current_user)
        password_form = ChangePassword(current_user, request.POST)

        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            password_form.save()
            messages.success(request, "Профиль и пароль успешно обновлены")
            login(request, current_user)  # обновить сессию после смены пароля
            return redirect('home')
        else:
            pass
    else:
        user_form = UpdateUserForm(instance=current_user)
        password_form = ChangePassword(current_user)

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'update_user.html', context)


def category_summary(request):
        categories = Category.objects.all()
        return render(request, 'category_summary.html', {"categories":categories})
     
def category(request, foo):
#заменить дефис пробелами
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, "Такой категории не существует")
        return redirect('home') 

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product}) 
from django.db.models import Min, Max

def home(request):
    products = Product.objects.all()

    max_price_input = request.GET.get('max_price')
    manual_price = request.GET.get('manual_price')

    if manual_price:
        products = products.filter(price__lte=manual_price)
    elif max_price_input:
        products = products.filter(price__lte=max_price_input)

    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(categories__name__in=selected_categories).distinct()

    price_range = Product.objects.aggregate(Min('price'), Max('price'))
    min_price = price_range['price__min'] or 0
    max_price = price_range['price__max'] or 0
    slider_images = [
    static('img/9.jpg'),
    static('img/1.png'),
    static('img/slider.jpg'),
    static('img/4.jpg'),
    static('img/0.jpg'),
    

]
    return render(request, 'home.html', {
        'products': products,
        'slider_images': slider_images
    })
    context = {
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
        'categories': Category.objects.all(),
        'selected_max_price': manual_price or max_price_input or max_price,
        'selected_categories': selected_categories,
        'slider_images': slider_images  # <== добавлено
    }

    return render(request, 'home.html', context)

def catalog(request):
    products = Product.objects.all()
    
    # Получаем диапазон цен
    price_range = Product.objects.aggregate(Min('price'), Max('price'))
    min_price = price_range['price__min'] or 0
    max_price = price_range['price__max'] or 0
    
    # Обработка минимальной цены
    selected_min_price = request.GET.get('min_price', min_price)
    try:
        selected_min_price = float(selected_min_price)
        if selected_min_price < min_price:
            selected_min_price = min_price
    except (ValueError, TypeError):
        selected_min_price = min_price
    
    # Обработка максимальной цены
    selected_max_price = request.GET.get('max_price', max_price)
    try:
        selected_max_price = float(selected_max_price)
        if selected_max_price > max_price:
            selected_max_price = max_price
    except (ValueError, TypeError):
        selected_max_price = max_price
    
    # Фильтрация по цене
    products = products.filter(price__gte=selected_min_price, price__lte=selected_max_price)
    
    # Остальные фильтры (категории, бренды)
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(categories__name__in=selected_categories).distinct()
    
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__brand_name__in=selected_brands)
    
    context = {
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
        'selected_min_price': selected_min_price,
        'selected_max_price': selected_max_price,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all().order_by('brand_name'),
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
    }
    
    return render(request, 'catalog.html', context)

def search_products_api(request):
    """API для поиска товаров по характеристикам"""
    if request.method == 'GET':
        try:
            # Получаем параметры поиска
            color = request.GET.get('color', '').lower()
            category = request.GET.get('category', '')
            tags = request.GET.get('tags', '').split(',') if request.GET.get('tags') else []
            limit = int(request.GET.get('limit', 6))
            
            # Начинаем с всех товаров
            products = Product.objects.all()
            
            # Фильтруем по цвету
            if color:
                # Маппинг русских названий цветов на английские
                color_map = {
                    'красный': 'red', 'красное': 'red',
                    'синий': 'blue', 'синее': 'blue',
                    'зеленый': 'green', 'зеленое': 'green',
                    'желтый': 'yellow', 'желтое': 'yellow',
                    'белый': 'white', 'белое': 'white',
                    'черный': 'black', 'черное': 'black',
                    'розовый': 'pink', 'розовое': 'pink',
                    'фиолетовый': 'purple', 'фиолетовое': 'purple',
                    'оранжевый': 'orange', 'оранжевое': 'orange',
                    'коричневый': 'brown', 'коричневое': 'brown',
                    'золотой': 'gold', 'золотое': 'gold',
                    'серебряный': 'silver', 'серебряное': 'silver',
                }
                color_en = color_map.get(color, color)
                products = products.filter(color=color_en)
            
            # Фильтруем по категории
            if category:
                products = products.filter(category__name__icontains=category)
            
            # Фильтруем по тегам
            if tags:
                products = products.filter(tags__name__in=tags).distinct()
            
            # Ограничиваем количество
            products = products[:limit]
            
            # Формируем ответ
            products_data = []
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'color': product.get_color_display() if product.color else 'Не указан',
                    'category': product.category.name if product.category else '',
                    'image_url': request.build_absolute_uri(product.image.url) if product.image else '',
                    'url': request.build_absolute_uri(f'/product/{product.id}'),
                })
            
            return JsonResponse({
                'count': len(products_data),
                'products': products_data,
                'filters': {
                    'color': color,
                    'category': category,
                    'tags': tags,
                }
            })
            
        except Exception as e:
            print(f"Ошибка поиска товаров: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only GET method allowed'}, status=405)

def about(request):
        return render(request, 'about.html', {})

def login_user(request):
        if request.method == "POST":
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                        login(request, user)

                        current_user = Profile.objects.get(user__id=request.user.id)
                        saved_cart = current_user.old_cart
                        if saved_cart:
                                converted_cart=json.loads(saved_cart)
                                cart = Cart(request)
                                for key, value in converted_cart.items():
                                        cart.db_add(product=key, quantity=value)



                        messages.success(request, ("Вы успешно вошли в систему"))
                        return redirect('home')
                else:
                        messages.success(request, ("Произошла ошибка, пожалуйста, попробуйте еще раз"))
                        return redirect('login')
        else:
                return render(request, 'login.html', {})

def logout_user(request):
      logout(request)
      messages.success(request, ("Вы вышли из системы"))
      return redirect('home')

def register_user(request):

 form=SignUpForm()
 if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
        #вход как пользователь
                user = authenticate(username = username, password=password)
                login(request, user)
                messages.success(request, ("Имя пользователя успешно создано! Пожалуйста, заполните все данные ниже"))
                return redirect('update_info')
        else:
                messages.success(request, ("упс! Ошибка регистрации, пожалуйста, попробуйте еще раз"))
                return redirect('register')
 else:
        return render(request, 'register.html', {'form':form})
 


openai.api_key = settings.OPENAI_API_KEY






def analyze_user_query(user_message):
    """Анализирует запрос пользователя и извлекает ключевые параметры"""
    
    query_params = {
        'colors': [],
        'materials': [],
        'events': [],
        'styles': [],
        'price_range': None,
        'product_types': []
    }
    
    # Цвета 
    color_mapping = {
        'красн': 'red', 'алый': 'red', 'бордов': 'red', 'малинов': 'red',
        'син': 'blue', 'голуб': 'blue', 'лазур': 'blue', 'бирюзов': 'blue',
        'зелен': 'green', 'изумруд': 'green', 'салат': 'green', 'оливков': 'green',
        'желт': 'yellow', 'лимон': 'yellow', 'золот': 'gold', 'золото': 'gold',
        'оранж': 'orange', 'кораллов': 'orange',
        'фиолет': 'purple', 'сиренев': 'purple', 'лилов': 'purple',
        'розов': 'pink', 'фукси': 'pink',
        'коричнев': 'brown', 'шоколад': 'brown', 'терракот': 'brown',
        'черн': 'black', 
        'бел': 'white', 'молоч': 'white', 'снеж': 'white',
        'сер': 'silver', 'серебр': 'silver', 'металл': 'silver',
        'многоцвет': 'multi', 'разноцвет': 'multi', 'ярк': 'multi'
    }
    
    # Материалы
    materials = [
        'золото', 'серебро', 'бархат', 'латунь', 'хлопок', 'шелк', 
        'парча', 'атлас', 'шерсть', 'мех', 'кожа', 'дерево',
        'керамика', 'фарфор', 'стекло', 'жемчуг', 'бирюза', 'сердолик'
    ]
    
    # События
    events = ['сабантуй', 'свадьба', 'науруз', 'курбан', 'рамадан', 
              'праздник', 'фестиваль', 'театр', 'концерт', 'вечеринка']
    
    # Стили
    styles = ['татарский', 'национальный', 'традиционный', 'современный',
              'классический', 'этнический', 'восточный', 'восточно-европейский']
    
    # Типы товаров
    product_types = ['серьги', 'колье', 'браслет', 'ожерелье', 'брошь',
                     'платье', 'костюм', 'тюбетейка', 'калфак', 'ичиги',
                     'футболка', 'рубашка', 'халат', 'пояс', 'сумка']
    
    # Извлекаем цвета
    for rus_color, eng_color in color_mapping.items():
        if rus_color in user_message:
            query_params['colors'].append(eng_color)
    
    #  материалы
    for material in materials:
        if material in user_message:
            query_params['materials'].append(material)
    
    #  события
    for event in events:
        if event in user_message:
            query_params['events'].append(event)
    
    #  стили
    for style in styles:
        if style in user_message:
            query_params['styles'].append(style)
    
    #типы товаров
    for product_type in product_types:
        if product_type in user_message:
            query_params['product_types'].append(product_type)
    
    # ценовой диапазон
    price_patterns = [
        (r'до\s*(\d+)', lambda x: (0, int(x))),  
        (r'от\s*(\d+)', lambda x: (int(x), 100000)), 
        (r'(\d+)\s*-\s*(\d+)', lambda x, y: (int(x), int(y)))  
    ]
    
    for pattern, func in price_patterns:
        match = re.search(pattern, user_message)
        if match:
            query_params['price_range'] = func(*match.groups())
            break
    
    return query_params


@csrf_exempt
def chat_with_assistant(request):
    """AI-консультант с сохранением истории в сессии"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
            session_id = data.get('session_id', '')
            
            print(f"[AI] Запрос: {user_message}")
            print(f"[AI] Session ID: {session_id}")
            
            # Проверка на осмысленность запроса
            if not is_meaningful_query(user_message):
                return JsonResponse({
                    'reply': 'Извините, я не совсем понял ваш запрос. Можете уточнить, что вы ищете? Например: "платье на свадьбу" или "золотые серьги".',
                    'suggested_products': [],
                    'style_advice': ''
                })
            
            # Анализируем запрос
            query_params = analyze_user_query(user_message)
            print(f"[AI] Параметры запроса: {query_params}")
            
            Product = apps.get_model('store', 'Product')
            
            # Формируем сложный запрос к базе данных
            products_query = Product.objects.all()
            
            # Создаем Q-объекты для каждого параметра
            q_objects = Q()
            
            # Фильтр по цветам
            if query_params['colors']:
                q_objects |= Q(color__in=query_params['colors'])
            
            # Фильтр по материалам
            if query_params['materials']:
                material_q = Q()
                for material in query_params['materials']:
                    material_q |= Q(material__icontains=material) | Q(description__icontains=material)
                q_objects &= material_q
            
            # Фильтр по событиям (через теги)
            if query_params['events']:
                event_q = Q()
                for event in query_params['events']:
                    event_q |= Q(tags__name__icontains=event)
                q_objects &= event_q
            
            # Фильтр по стилям
            if query_params['styles']:
                style_q = Q()
                for style in query_params['styles']:
                    style_q |= Q(tags__name__icontains=style) | Q(description__icontains=style)
                q_objects &= style_q
            
            # Фильтр по типам товаров
            if query_params['product_types']:
                type_q = Q()
                for product_type in query_params['product_types']:
                    type_q |= Q(name__icontains=product_type) | Q(description__icontains=product_type) | Q(tags__name__icontains=product_type)
                q_objects &= type_q
            
            # Фильтр по цене
            if query_params['price_range']:
                min_price, max_price = query_params['price_range']
                q_objects &= Q(price__gte=min_price) & Q(price__lte=max_price)
            
            # Применяем фильтры
            if q_objects:
                products_query = products_query.filter(q_objects).distinct()
            
            # Сортируем по релевантности
            products_query = products_query.order_by('-is_sale', 'price')
            
            # Если найдено мало товаров, расширяем поиск ТОЛЬКО если запрос осмысленный
            found_products = list(products_query[:4])
            
            # Проверяем, есть ли вообще параметры для поиска
            has_search_params = any([
                query_params['colors'],
                query_params['materials'], 
                query_params['events'],
                query_params['styles'],
                query_params['product_types'],
                query_params['price_range']
            ])
            
            if len(found_products) < 3 and has_search_params:
                # Расширяем поиск только если есть параметры для поиска
                print(f"[AI] Расширяю поиск, найдено {len(found_products)} товаров")
                backup_products = Product.objects.filter(
                    Q(description__icontains=user_message[:10]) |
                    Q(name__icontains=user_message[:10])
                )[:6]
                found_products.extend(backup_products)
                found_products = list(set(found_products))[:4]
            elif not has_search_params:
                print(f"[AI] Нет параметров для поиска, не расширяю")
            
            # Генерируем персонализированный ответ
            reply_message = generate_personalized_reply(query_params, user_message, len(found_products))
            
            # Если нет товаров и нет параметров поиска
            if len(found_products) == 0 and not has_search_params:
                reply_message = """Извините, я не совсем понял ваш запрос. 

Попробуйте задать вопрос более конкретно, например:
• "Подбери платье на свадьбу"
• "Нужны золотые серьги в татарском стиле"
• "Что надеть на Сабантуй?"
• "Ищу тюбетейку для подарка"

Я помогу подобрать идеальный образ!"""
            
            # Формируем данные о товарах
            suggested_products = []
            for product in found_products:
                # Получаем теги с категориями
                tags_with_categories = []
                for tag in product.tags.select_related('category').all():
                    category_name = tag.category.get_name_display() if tag.category else 'Общие'
                    tags_with_categories.append(f"{category_name}: {tag.name}")
                
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'sale_price': str(product.sale_price) if product.is_sale else None,
                    'material': product.material or 'Не указан',
                    'color': product.get_color_display() if product.color else 'Не указан',
                    'description': product.description,
                    'tags': tags_with_categories[:3],
                    'is_sale': product.is_sale,
                    'image_url': request.build_absolute_uri(product.image.url) if product.image else '',
                    'url': f'/product/{product.id}',
                }
                suggested_products.append(product_data)
            
            # Если товары найдены, добавляем советы по стилю
            style_advice = generate_style_advice(query_params, suggested_products)
            
            # Если есть товары и настроен GPT - получаем совет от GPT
            if suggested_products and hasattr(settings, 'OPENAI_API_KEY'):
                try:
                    gpt_advice = get_gpt_advice(user_message, suggested_products[:2])
                    if gpt_advice:
                        reply_message += f"\n\n{gpt_advice}"
                except Exception as e:
                    print(f"[AI] GPT ошибка: {e}")
            
            # Сохраняем в сессии Django
            if 'chat_history' not in request.session:
                request.session['chat_history'] = []
            
            # Добавляем текущий диалог в историю сессии
            request.session['chat_history'].append({
                'user': user_message,
                'assistant': reply_message,
                'products_count': len(suggested_products)
            })
            
            # Ограничиваем историю
            if len(request.session['chat_history']) > 10:
                request.session['chat_history'] = request.session['chat_history'][-10:]
            
            request.session.modified = True
            
            return JsonResponse({
                'reply': reply_message,
                'style_advice': style_advice,
                'suggested_products': suggested_products,
                'count': len(suggested_products),
                'session_id': session_id,
            })
            
        except Exception as e:
            print(f"[AI] Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'reply': 'Извините, произошла ошибка. Попробуйте уточнить ваш запрос.',
                'suggested_products': []
            })
    
    return JsonResponse({'status': 'active'})

def is_meaningful_query(user_message):
    """
    Проверяет, является ли запрос осмысленным
    Возвращает True если найдены ключевые слова, False если нет
    """
    
    # Минимальная длина осмысленного запроса
    if len(user_message) < 3:
        return False
    
    # Ключевые слова, которые делают запрос осмысленным
    meaningful_keywords = [
        # События
        'театр', 'свадьба', 'сабантуй', 'праздник', 'фестиваль', 'концерт',
        'повседневный', 'офис', 'работа', 'прогулка', 'вечеринка',
        
        # Типы товаров
        'платье', 'костюм', 'рубашка', 'футболка', 'блузка', 'юбка', 'брюки',
        'серьги', 'колье', 'браслет', 'кольцо', 'ожерелье', 'брошь',
        'тюбетейка', 'калфак', 'ичиги', 'халат', 'пояс', 'сумка',
        
        # Цвета
        'красный', 'синий', 'зеленый', 'желтый', 'черный', 'белый', 
        'золотой', 'серебряный', 'розовый', 'фиолетовый',
        
        # Материалы
        'золото', 'серебро', 'шелк', 'хлопок', 'бархат', 'кожа',
        
        # Действия
        'подбери', 'посоветуй', 'помоги', 'хочу', 'нужен', 'ищу',
        'купить', 'выбрать', 'найти', 'образ', 'наряд',
        
        # Стили
        'татарский', 'национальный', 'традиционный', 'современный'
    ]
    
    # Дополнительные проверки для русского языка
    # Проверяем, содержит ли запрос хотя бы 2 осмысленных слова
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    
    # Проверка на слишком много согласных подряд 
    consonants = 'бвгджзйклмнпрстфхцчшщ'
    if len(user_message) > 10:
        max_consonants_in_row = 0
        current_consonants = 0
        
        for char in user_message:
            if char in consonants:
                current_consonants += 1
                max_consonants_in_row = max(max_consonants_in_row, current_consonants)
            else:
                current_consonants = 0
        
        # Если есть 5+ согласных подряд - скорее всего бессмыслица
        if max_consonants_in_row >= 5:
            return False
    
    # Проверяем наличие ключевых слов
    found_keywords = 0
    for keyword in meaningful_keywords:
        if keyword in user_message:
            found_keywords += 1
    
    # Если запрос слишком короткий и не содержит ключевых слов
    if found_keywords == 0 and len(user_message) < 15:
        # Проверяем, есть ли в запросе хотя бы 50% русских букв
        russian_count = sum(1 for char in user_message if char in russian_letters)
        russian_percentage = (russian_count / len(user_message)) * 100
        
        if russian_percentage < 50:
            return False
        
        # Проверяем, похож ли запрос на осмысленное предложение
        words = user_message.split()
        if len(words) >= 2:
            # Если есть 2+ слова, проверяем их длину
            meaningful_words = sum(1 for word in words if len(word) >= 3)
            if meaningful_words < 1:
                return False
        else:
            # Если одно слово, оно должно быть достаточно длинным
            if len(user_message) < 4:
                return False
    
    print(f"[AI] Запрос осмысленный, найдено ключевых слов: {found_keywords}")
    return True

def generate_personalized_reply(query_params, user_message, product_count):
    """Генерирует персонализированный ответ"""
    
    greetings = ["Сәлам! ", "Исәнмесез! "]
    greeting = random.choice(greetings)
    
    # Проверяем, есть ли параметры поиска
    has_params = any([
        query_params['colors'],
        query_params['materials'], 
        query_params['events'],
        query_params['styles'],
        query_params['product_types']
    ])
    
    if not has_params and product_count == 0:
        return "Извините, я не совсем понял ваш запрос. Можете уточнить, что вы ищете?"
    
    reply_parts = [greeting]
    
    if any(keyword in user_message for keyword in ['подбери', 'посоветуй', 'выбери', 'помоги', 'найди']):
        reply_parts.append("Я помогу Вам подобрать идеальный образ. ")
    
    if product_count > 0:
        if product_count == 1:
            reply_parts.append(f"Нашел 1 подходящий товар. ")
        elif product_count <= 3:
            reply_parts.append(f"Нашел {product_count} подходящих товара. ")
        else:
            reply_parts.append(f"Нашел {product_count} подходящих товаров. ")
    else:
        if has_params:
            reply_parts.append("К сожалению, по Вашему запросу не найдено товаров. ")
        else:
            reply_parts.append("Не совсем понял ваш запрос. ")
            reply_parts.append("Уточните, пожалуйста, что вы ищете? Например: 'татарское платье' или 'серебряные серьги'.")
        return ''.join(reply_parts)
    
    if query_params['events']:
        event = query_params['events'][0]
        event_advice = {
            'сабантуй': "Для Сабантуя выбирайте яркие, праздничные цвета и удобные ткани. Прекрасно подойдут традиционные платья и украшения.",
            'свадьба': "Для свадьбы подойдут элегантные и нарядные украшения из золота или серебра с национальными орнаментами.",
            'театр': "Для похода в театр выбирайте сдержанные, элегантные аксессуары. Классическое платье с татарским орнаментом будет идеальным выбором.",
            'повседневный': "Для повседневной носки выбирайте удобные и практичные вещи с элементами национального стиля.",
            'праздничный': "Для праздничного мероприятия подойдут яркие цвета и богато украшенные изделия.",
            'фестиваль': "Для фестиваля можно выбрать яркие, запоминающиеся наряды и украшения."
        }
        reply_parts.append(event_advice.get(event, ""))
    
    if query_params['materials']:
        materials = ', '.join(query_params['materials'][:2])
    
    
    return ''.join(reply_parts)

def generate_style_advice(query_params, products):
    """Генерирует советы по стилю"""
    
    if not products:
        return ""
    
    advice_parts = []
    
    if query_params.get('colors'):
        colors = query_params['colors']
        if 'gold' in colors:
            advice_parts.append("Золотые акценты отлично сочетаются с черным, белым и темно-синим.")
        if 'silver' in colors:
            advice_parts.append("Серебряные украшения хорошо смотрятся с холодными оттенками.")
        if 'red' in colors:
            advice_parts.append("Красный - цвет энергии, отлично сочетается с нейтральными тонами.")
    
    materials_in_products = set(p['material'] for p in products if p['material'] != 'Не указан')
    for material in materials_in_products:
        if 'золото' in material.lower():
            advice_parts.append("Золотые украшения требуют бережного ухода. Храните отдельно от других металлов.")
        if 'серебро' in material.lower():
            advice_parts.append("Серебро может темнеть со временем. Используйте специальные салфетки для чистки.")
        if 'бархат' in material.lower():
            advice_parts.append("Бархатные вещи лучше стирать вручную или в деликатном режиме.")
    
    return " | ".join(advice_parts) if advice_parts else ""



def get_gpt_advice(user_query, context_products):
    """Получает советы от GPT API"""
    
    try:
        openai.api_key = settings.OPENAI_API_KEY
        
        product_descriptions = []
        for product in context_products[:2]:
            desc = f"- {product['name']}: {product['color']}, {product['material']}, цена: {product['price']} руб."
            if product.get('tags'):
                desc += f", теги: {', '.join(product['tags'][:2])}"
            product_descriptions.append(desc)
        
        prompt = f"""
        Ты - стилист-консультант магазина татарских товаров. 
        Пользователь спрашивает: "{user_query}"
        
        Я нашел следующие товары:
        {chr(10).join(product_descriptions)}
        
        Дай краткий, дружелюбный совет (1-2 предложения) по стилю с учетом татарских традиций.
        Используй иногда татарские слова.
        Не упоминай конкретные товары в ответе, дай общий стилистический совет.
        Ответь на русском языке.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты стилист-консультант магазина татарских товаров."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"GPT Error: {e}")
        return ""


def clear_chat_history(request):
    """Очистка истории чата в сессии"""
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return JsonResponse({'status': 'history cleared'})



def historical_articles(request):
    """Список всех исторических статей"""
    articles = HistoricalArticle.objects.all()
    
    # Фильтрация по типу
    article_type = request.GET.get('type')
    if article_type:
        articles = articles.filter(article_type=article_type)
    
    # Получаем имя выбранного типа для отображения
    selected_type_name = None
    if article_type:
        for code, name in HistoricalArticle.ARTICLE_TYPES:
            if code == article_type:
                selected_type_name = name
                break
    
    context = {
        'articles': articles, 
        'article_types': HistoricalArticle.ARTICLE_TYPES,
        'selected_type': article_type,
        'selected_type_name': selected_type_name,
        'total_articles': articles.count(),
    }
    
    return render(request, 'historical_articles.html', context)
def article_detail(request, article_id):
    article = get_object_or_404(HistoricalArticle, id=article_id)
    
    # Похожие статьи
    similar_articles = HistoricalArticle.objects.filter(
        article_type=article.article_type,
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'similar_articles': similar_articles,
    }
    
    return render(request, 'article_detail.html', context)

