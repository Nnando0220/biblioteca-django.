from django.urls import path, include
from . import views

urlpatterns = [
    path('livros/', views.LivroList.as_view(), name='livro-list'),
    path('livros/<int:pk>/', views.LivroDetail.as_view(), name='livro-detail'),
    path('categoria/', views.CategoriaList.as_view(), name='categoria-list'),
    path('categoria/<int:pk>/', views.CategoriaDetail.as_view(), name='categoria-detail'),
    path('autor/', views.AutorList.as_view(), name='autor-list'),
    path('autor/<int:pk>/', views.AutorDetail.as_view(), name='autor-detail'),
    path('', views.ApiRoot.as_view(), name='api-root'),
]
