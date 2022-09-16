from django.urls import path

from .views import *

app_name = 'base'

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('logout/', logout_user, name='logout'),
    path('', home, name='home'),
    path('room/<int:pk>/', room, name='room'),
    path('profile/<int:pk>/', user_profile, name='profile'),
    path('create/', create_room, name='create_room'),
    path('update/<int:pk>/', update_room, name='update_room'),
    path('delete/<int:pk>/', delete_room, name='delete_room'),
    path('delete_message/<int:pk>/', delete_message, name='delete_message'),
    path('update-user/', update_user, name='update_user'),
    path('topics/', topics_page, name='topics'),
    path('activities/', activities_page, name='activities'),
]