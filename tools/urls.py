"""Secret_We URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.visualize, name='tools'),
    path(r'visual', views.visualize, name='visual'),
    path(r'visual/', views.visualize, name='visual'),
    path(r'visual/result', views.show_result, name='visual_result'),
    path(r'visual/result/', views.show_result, name='visual_result'),
    path(r'visual/result/download', views.download, name='visual_result'),
    path(r'visual/result/download/', views.download, name='visual_result'),
    path(r'visual/example', views.examples, name='visual_examples'),
    path(r'visual/example/', views.examples, name='visual_examples'),
    path(r'dimension', views.dimension, name='dimension_reduction'),
    path(r'dimension/', views.dimension, name='dimension_reduction'),
    path(r'cluster/', views.cluster, name='cluster'),
    path(r'cluster', views.cluster, name='cluster'),
]
