from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, PasswordResetToken, Supplier, Product, InvoiceProduct, Invoice, StockMovement


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("password",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "middle_name", "email", "phone_number")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "avatar"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name", "last_name", "middle_name", "email", "dial_in_code", "phone_number",
                    "usable_password", "password1", "password2", "is_staff", "is_superuser", "avatar"
                ),
            },
        ),
    )

    list_display_links = ("email", "phone_number")
    list_display = ("id", "email", "phone_number", "full_name", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("-id",)
    filter_horizontal = ["groups"]


@admin.register(PasswordResetToken)
class PWResetTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'supplier',
        'product_unit',
        'threshold_value',
        'unit_price',
        'stock_value',
        'qr_code',
        'status'
    ]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone_number", "email")


class InvoiceProductInline(admin.TabularInline):
    model = InvoiceProduct
    fields = ['product', 'quantity']
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'invoice_number',
        'customer_name',
        'customer_contact',
        'total',
        'invoice_status',
        'date_paid',
        'date_supplied',
        'status'
    ]
    inlines = (InvoiceProductInline,)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'date',
        'product',
        'invoice',
        'movement_type',
        'stock_before',
        'quantity',
        'stock_after',
        'user'
    ]
