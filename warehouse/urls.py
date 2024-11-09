
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
    path('auth/users/', views.UserListView.as_view(), name='user_list'),
    path('auth/users/<pk>/', views.UserRetrieveView.as_view(), name='user_retrieve'),
    path('auth/get-roles/', views.get_roles, name='get_roles'),
    path('warehouse/suppliers/', views.SupplierListView.as_view(), name='suppliers_list'),
    path('warehouse/suppliers/<pk>', views.SupplierDetailView.as_view(), name='suppliers_detail'),
    path('warehouse/products/', views.ProductListView.as_view(), name='products_list'),
    path('warehouse/products/<pk>', views.ProductDetailView.as_view(), name='products_detail'),
    path('warehouse/stock-update/<product_id>/<quantity>/<change_type>', views.stock_update, name='stock_update'),
    path('warehouse/stock-movement/', views.StockMovementListView.as_view(), name='stock_movement_list'),
    path('warehouse/invoices-create/', views.create_invoice, name='stock_update'),
    path('warehouse/invoices-list/', views.list_invoices, name='stock_update'),
    path('warehouse/invoices-retrieve/<pk>/', views.retrieve_invoice, name='retrieve_invoice'),
    path('warehouse/invoices-update/<pk>/', views.update_invoice, name='update_invoice'),
    path('warehouse/invoices-delete/<pk>/', views.delete_invoice, name='delete_invoice'),
    path('warehouse/invoices-payment/<pk>/', views.pay_invoice, name='pay_invoice'),
    path('warehouse/invoices-supply/<pk>/', views.supply_invoice, name='supply_invoice'),
]
