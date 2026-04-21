from django.urls import path
from . import views
from .views import (
    historical_articles, article_detail, )

urlpatterns = [
    path('', views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('login/', views.login_user, name = 'login'),
    path('logout/', views.logout_user, name = 'logout'),
    path('register/', views.register_user, name = 'register'),
    path('update_password/', views.update_password, name = 'update_password'),
    path('update_user/', views.update_user, name = 'update_user'),
    path('update_info/', views.update_info, name = 'update_info'),
    path('product/<int:pk>', views.product, name = 'product'),
    path('category/<str:foo>', views.category, name = 'category'),
    path('category_summary/<str:foo>', views.category_summary, name = 'category_summary'),
    path('search/', views.search, name = 'search'),
    path('catalog/', views.catalog, name = 'catalog'),
    path('assistant/chat/', views.chat_with_assistant, name='assistant_chat'),
    path('assistant/clear/', views.clear_chat_history, name='clear_chat'),
    path('api/search-products/', views.search_products_api, name='search_products_api'),
    path('api/chat-history/', views.get_chat_history, name='get_chat_history'),
    path('api/chat-clear/', views.clear_chat_history_db, name='clear_chat_history_db'),
    path('culture/', historical_articles, name='historical_articles'),
    path('culture/article/<int:article_id>/', article_detail, name='article_detail'),

]
