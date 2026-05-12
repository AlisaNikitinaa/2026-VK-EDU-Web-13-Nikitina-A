from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('ask/', views.ask_view, name='ask_form'),
    path('question/<int:pk>/add_answer/', views.add_answer_view, name='add_answer'),
    path('question/<int:pk>/like/', views.question_like_view, name='question_like'),
    path('answer/<int:pk>/like/', views.answer_like_view, name='answer_like'),
    path('answer/<int:pk>/correct/', views.answer_correct_view, name='answer_correct'),
]