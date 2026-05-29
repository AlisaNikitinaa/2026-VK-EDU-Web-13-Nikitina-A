from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include('core.urls')),
    path('', views.index, name='index'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('question/<int:pk>/', views.question, name='one_question'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('search/', views.search, name='search'),  # НОВОЕ
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)