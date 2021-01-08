from django.urls import path
from . import views

urlpatterns = [
    
    path('registration/',views.registration_page,name='registration_page'), 
    path('login/',views.login_page,name='login_page'), 
    path('logout/',views.user_logout,name='user_logout')
    ]
