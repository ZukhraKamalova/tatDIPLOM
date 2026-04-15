from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
from django.urls import reverse
from django.conf import settings
import uuid


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect
from django.contrib import messages

def send_order_confirmation_email(email, order_details):
   
    try:
        subject = f'Ваш заказ №{order_details["order_id"]} принят в обработку'
        
        # Рендерим HTML шаблон
        html_message = render_to_string('payment/order_confirmation.html', {
            'order_details': order_details,
        })
        plain_message = strip_tags(html_message)
        
        # Отправляем письмо
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='zukhrakamal@mail.ru',
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Логируем успех
        print(f"[EMAIL] Успешно отправлено на {email}")
        return True
        
    except Exception as e:
        # Логируем ошибку
        print(f"[EMAIL] ОШИБКА отправки на {email}: {str(e)}")
        return False
    
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()    
                order.update(shipped=True, date_shipped=now)
            else:
                order = Order.objects.filter(id=pk)
                order.update(shipped=False)
            messages.success(request, "Статус доставки обновлен")
            return redirect('home')
        return render(request, 'payment/orders.html', {"order":order, "items":items})
    else:
        messages.success(request, "Доступ запрещен")
        return redirect('home')
    
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()    
            order.update(shipped=True, date_shipped=now)
    
            messages.success(request, "Статус доставки обновлен")
            return redirect('home')
        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, 'Доступ запрещен')
        return redirect('home')
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()    
            order.update(shipped=False)
            messages.success(request, "Статус доставки обновлен")
            return redirect('home')
        return render(request, "payment/shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, 'Доступ запрещен')
        return redirect('home')

def process_order(request):
    if request.method != 'POST':
        messages.error(request, 'Некорректный метод запроса')
        return redirect('home')

    try:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # Получаем данные доставки из сессии
        my_shipping = request.session.get('my_shipping')
        if not my_shipping:
            messages.error(request, 'Данные доставки не найдены')
            return redirect('checkout')

        # Подготавливаем данные заказа
        order_data = {
            'full_name': my_shipping['shipping_full_name'],
            'email': my_shipping['shipping_email'],
            'shipping_address': f"{my_shipping['shipping_address']}\n{my_shipping['shipping_city']}",
            'amount_paid': totals,
        }

        # Создаем заказ
        if request.user.is_authenticated:
            order = Order(user=request.user, **order_data)
        else:
            order = Order(**order_data)
        
        order.save()

        # Создаем позиции заказа
        for product in cart_products:
            price = product.sale_price if product.is_sale else product.price
            
            for key, value in quantities.items():
                if int(key) == product.id:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        user=request.user if request.user.is_authenticated else None,
                        quantity=value,
                        price=price
                    )

        # Подготовка данных для письма
        order_details = {
            'order_id': order.id,
            'products': [],
            'total': totals,
            'shipping_info': {
                'shipping_full_name': my_shipping['shipping_full_name'],
                'shipping_address': my_shipping['shipping_address'],
                'shipping_city': my_shipping['shipping_city'],
            },
            'date_ordered': order.date_ordered.strftime('%d.%m.%Y %H:%M'),
        }

        for item in order.orderitem_set.all():
            order_details['products'].append({
                'name': item.product.name,
                'price': item.price,
                'quantity': item.quantity,
                'subtotal': item.price * item.quantity,
            })

        # Отправка email
        email_sent = send_order_confirmation_email(order.email, order_details)
        
        if email_sent:
            messages.success(
                request, 
                f'Заказ №{order.id} успешно оформлен! Подтверждение отправлено на {order.email}'
            )
        else:
            messages.warning(
                request, 
                f'Заказ №{order.id} оформлен, но не удалось отправить подтверждение на {order.email}.'
            )

        # Очистка корзины и сессии
        if request.user.is_authenticated:
            Profile.objects.filter(user=request.user).update(old_cart="")
        
        for key in list(request.session.keys()):
            if key == "session_key":
                del request.session[key]
        
        if 'my_shipping' in request.session:
            del request.session['my_shipping']

        return redirect('home')

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка обработки заказа: {str(e)}")
        
        messages.error(
            request, 
            f'Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте еще раз.'
        )
        return redirect('checkout')
    
def billing_info(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart_products = cart.get_prods()  
        quantities = cart.get_quants()    
        totals = cart.cart_total()

        # Сохраняем данные доставки в сессию
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        billing_form = PaymentForm()
        
        return render(request, "payment/billing_info.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_info": my_shipping,
            "billing_form": billing_form
        })
    else:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')
def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()  
    quantities = cart.get_quants()    
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        try:
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            shipping_form = ShippingForm(request.POST or None)
    else:
        shipping_form = ShippingForm(request.POST or None)
    
    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form
    })
    
   
def payment_success(request):
    return render(request, "payment/payment_success.html", {})
