
from django.urls import path

from . import views
urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/initiate-password-reset/<email>/', views.initiate_password_reset, name='reset_init'),
    path('auth/token-status/<token>/', views.password_reset_token_status, name='token_status'),
    path('auth/complete-password-reset/', views.complete_password_reset, name='reset_complete'),
    path('auth/change-password/', views.change_password, name='change_complete'),
    path('auth/manage-user/', views.manage_user, name='manage_user'),
    path('auth/get-roles/', views.get_roles, name='get_roles')
]
