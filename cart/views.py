from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()
	return render(request, "cart_summary.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals})

def cart_add(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
	
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		product = get_object_or_404(Product, id=product_id)
		
		# Save to session
		cart.add(product=product, quantity=product_qty)

		# Get Cart Quantity
		cart_quantity = cart.__len__()

		response = JsonResponse({'qty': cart_quantity})
		messages.success(request, ("Товар добавлен в корзину"))
		return response

def cart_delete(request):
	cart = Cart(request)
	# Get stuff
	product_id = int(request.POST.get('product_id'))
	# Call delete Function in Cart
	cart.delete(product=product_id)

	response = JsonResponse({'product': product_id})
	messages.success(request, "Товар удален из корзины")
	return response



def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		cart.update(product=product_id, quantity=product_qty)

		totals = cart.cart_total()
		response = JsonResponse({'qty': product_qty, 'totals': totals})
		messages.success(request, "Ваша корзина обновлена")
		return response
	
def cart_total(self):
    return sum(float(item['price']) * item['qty'] for item in self.cart.values())

def cart_clear(request):
    cart = Cart(request)
    cart.clear()  # очищаем корзину
    messages.success(request, ("Корзина очищена"))
    return JsonResponse({'status': 'ok'})

