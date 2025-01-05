
import uuid
from _decimal import Decimal
from pathlib import Path

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from versatileimagefield.fields import VersatileImageField

from warehouse import utils

ACTIVE = 'Active'
INACTIVE = 'Inactive'
ACTIVITY_CHOICES = [(ACTIVE, ACTIVE), (INACTIVE, INACTIVE)]


def path_and_filename(instance, filename):
    upload_to = f'medias/{instance.__class__.__name__.lower()}'
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return Path(upload_to)/filename


class Country(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    iso_3166 = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField(_("Email address"), unique=True)
    dial_in_code = models.CharField(_("Dial_in code"), max_length=8, default="+234")
    phone_number = models.CharField(_("Phone number"), max_length=20, unique=True, null=True, blank=True )
    first_name = models.CharField(_("First name"), max_length=25, blank=True)
    middle_name = models.CharField(_("Middle name"), max_length=25, default='', blank=True)
    last_name = models.CharField(_("Last name"), max_length=25, blank=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    is_staff = models.BooleanField(_("Is staff"), default=False)
    is_superuser = models.BooleanField(default=False)
    avatar = VersatileImageField('avatar', null=True, blank=True, upload_to=path_and_filename)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        # Simplest possible answer: Yes, always
        return True

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class PasswordResetToken(TimeStampedModel):
    key = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')

    def __str__(self):
        return self.user.full_name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=9, choices=ACTIVITY_CHOICES, default=ACTIVE)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, related_name='products', on_delete=models.PROTECT)
    product_unit = models.CharField(max_length=50)
    threshold_value = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_value = models.FloatField()
    # qr_code = models.CharField(max_length=100)
    image = VersatileImageField('product_image', null=True, blank=True, upload_to=path_and_filename)
    status = models.CharField(max_length=9, choices=ACTIVITY_CHOICES, default=ACTIVE)

    def __str__(self):
        return f'{self.supplier.name}: {self.name}'


class InvoiceProduct(TimeStampedModel):
    product = models.ForeignKey(Product, related_name='invoice_products', on_delete=models.PROTECT)
    invoice = models.ForeignKey('Invoice', related_name='invoice_products', on_delete=models.PROTECT)
    quantity = models.FloatField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.cost = Decimal(self.quantity) * self.product.unit_price
        super().save(*args, **kwargs)
        self.invoice.total = sum(self.invoice.invoice_products.values_list('cost', flat=True))
        self.invoice.save()


class Invoice(TimeStampedModel):
    PENDING = 'Pending'
    PAID = 'Paid'
    DELIVERED = 'Delivered'
    INVOICE_STATUS_CHOICES = [(PENDING, PENDING), (PAID, PAID), (DELIVERED, DELIVERED)]
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    customer_name = models.CharField(max_length=255)
    customer_contact = models.CharField(max_length=15)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    invoice_status = models.CharField(max_length=9, choices=INVOICE_STATUS_CHOICES, default=PENDING)
    date_paid = models.DateTimeField(null=True, blank=True)
    date_supplied = models.DateTimeField(null=True, blank=True)
    products = models.ManyToManyField(Product, through=InvoiceProduct)
    status = models.CharField(max_length=9, choices=ACTIVITY_CHOICES, default=ACTIVE)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.invoice_number = utils.generate_invoice_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class StockMovement(TimeStampedModel):
    INCREASE = 'Increase'
    DECREASE = 'Decrease'
    MOVEMENT_TYPE_CHOICES = [(INCREASE, INCREASE), (DECREASE, DECREASE)]
    date = models.DateTimeField()
    product = models.ForeignKey(Product, related_name='stock_movements', on_delete=models.PROTECT)
    quantity = models.FloatField()
    movement_type = models.CharField(max_length=9, choices=MOVEMENT_TYPE_CHOICES)
    invoice = models.ForeignKey(Invoice, related_name='stock_movements', on_delete=models.PROTECT, blank=True, null=True)
    stock_before = models.FloatField()
    stock_after = models.FloatField()
    user = models.ForeignKey(User, related_name='stock_movements', on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        if self.movement_type == self.INCREASE:
            self.stock_after = self.stock_before + self.quantity
        else:
            self.stock_after = self.stock_before - self.quantity
        super().save(*args, **kwargs)
