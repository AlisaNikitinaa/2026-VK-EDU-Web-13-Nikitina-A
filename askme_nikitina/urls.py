"""
URL configuration for askme_nikitina project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ask/', views.ask_form, name='ask_form'),
    path('question/<int:question_id>/', views.question, name='one_question'),
    path('question/<int:question_id>/add_answer/', views.add_answer, name='add_answer'),
    path('profile/', views.profile, name='profile'),
    path('authorization/', views.authorization, name='authorization'),
    path('registration/', views.registration, name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('hot/', views.hot_questions, name='hot_questions'),
]
