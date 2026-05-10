from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', views.index, name='index'),
    path('ask/', views.ask_form, name='ask_form'),
    path('question/<int:pk>/', views.question, name='one_question'),
    path('question/<int:pk>/add_answer/', views.add_answer, name='add_answer'),
    path('profile/', views.profile, name='profile'),
    path('authorization/', views.authorization, name='authorization'),
    path('registration/', views.registration, name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('hot/', views.hot_questions, name='hot_questions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)