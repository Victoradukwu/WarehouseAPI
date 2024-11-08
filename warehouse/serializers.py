import datetime

from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from versatileimagefield.serializers import VersatileImageFieldSerializer

from . import models as all_models
from .models import User


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    avatar = VersatileImageFieldSerializer(read_only=True, allow_null=True, sizes='all_image_size')

    class Meta:
        model = all_models.User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'roles', 'avatar']

    @staticmethod
    def get_roles(instance):
        roles = [role.name for role in instance.groups.all()]
        return roles


class UserTokenSerializer(serializers.Serializer):

    user = UserSerializer()
    access_token = serializers.CharField(required=True)


class RegisterSerializer(serializers.Serializer):

    role = serializers.CharField(required=False)
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    avatar_file = serializers.FileField(required=False, write_only=True)

    class Meta:
        fields = UserSerializer.Meta.fields

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Password and Confirm password must be the same.')
        if 'avatar_file' in data:
            data['avatar'] = data.pop('avatar_file')
        super().validate(data)
        return data

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        _ = validated_data.pop('confirm_password')
        user = all_models.User.objects.create_user(**validated_data)
        if role:
            user.groups.add(Group.objects.get(name=role))
        token = Token.objects.create(user=user)

        return user, token


class LoginSerializer(serializers.Serializer):

    email = serializers.CharField(required=False)
    password = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):

    token = serializers.CharField(required=False)
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Password and Confirm password do not match.')
        super().validate(data)
        return data

    def save(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        token = validated_data.get('token')
        try:
            user = all_models.User.objects.get(email=email)
        except Exception:
            raise ValidationError('Password reset is not successful. Incorrect email.')

        if all_models.PasswordResetToken.objects.filter(user=user, key=token, status='Active').exists():
            user.set_password(password)
            user.save()
            all_models.PasswordResetToken.objects.filter(user=user, key=token).update(status='Inactive')


class PasswordChangeSerializer(serializers.Serializer):

    password = serializers.CharField()
    confirm_password = serializers.CharField()
    old_password = serializers.CharField()

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Password and Confirm password must be the same.')
        super().validate(data)
        return data

    def save(self):
        password = self.validated_data.get('password')
        old_password = self.validated_data.get('old_password')
        request = self.context.get('request')
        user = request.user
        if user.check_password(old_password):
            user.set_password(password)
            user.save()
        else:
            raise ValueError('Old password is incorrect')


class ManageUserSerializer(serializers.Serializer):
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    is_active = serializers.BooleanField(required=False)
    user_id = serializers.IntegerField()

    def save(self):
        roles = self.validated_data.get('roles')
        is_active = self.validated_data.get('is_active')
        user_id = self.validated_data.get('user_id')

        user = User.objects.get(id=user_id)
        if is_active:
            user.is_active = is_active
        if roles is not None:
            groups = Group.objects.filter(name__in=roles)
            user.groups.set(groups)
        user.save()


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = all_models.Supplier
        fields = ['id', 'name', 'email', 'phone_number']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = all_models.Product
        fields = ['id', 'name', 'supplier', 'product_unit', 'threshold_value', 'unit_price', 'stock_value', 'qr_code', 'image', 'status']


class StockMovementSerializer(serializers.ModelSerializer):

    class Meta:
        model = all_models.StockMovement
        fields = [
            'id',
            'date',
            'product',
            'quantity',
            'movement_type',
            'invoice',
            'stock_before',
            'stock_after',
            'user'
        ]


# class InvoiceProductSerializer(serializers.Serializer):
#     id =


class InvoiceSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = all_models.Invoice
        fields = [
            'id',
            'invoice_number',
            'customer_name',
            'customer_contact',
            'total',
            'invoice_status',
            'date_paid',
            'date_supplied',
            'products',
            'status',
            'created'
        ]

    def get_products(self, instance):
        return instance.invoice_products.values('id', 'product', 'quantity', 'cost', 'product__name')


class ItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.FloatField()


class InvoiceCreateSerializer(serializers.Serializer):
    products = serializers.ListField(child=ItemSerializer())
    customer_name = serializers.CharField()
    customer_contact = serializers.CharField()
    invoice_status = serializers.ChoiceField(choices=['Pending', 'Paid'], default='Pending')

    def save(self):
        data = self.validated_data
        products = data.pop('products', [])
        if data.get('invoice_status') == 'Paid':
            data['date_paid'] = datetime.datetime.now()
        invoice = all_models.Invoice.objects.create(**data)
        for item in products:
            all_models.InvoiceProduct.objects.create(**item, invoice=invoice)
        return invoice


class InvoiceUpdateSerializer(serializers.Serializer):
    products = serializers.ListField(child=ItemSerializer(), required=False)
    customer_name = serializers.CharField(required=False)
    customer_contact = serializers.CharField(required=False)

    @transaction.atomic
    def save(self):
        pk = self.context.get('pk')
        data = self.validated_data
        instance = all_models.Invoice.objects.filter(status=all_models.ACTIVE).get(id=pk)
        products = data.pop('products', [])
        if products:
            instance.invoice_products.all().delete()
            for item in products:
                all_models.InvoiceProduct.objects.create(**item, invoice=instance)
        for key, val in data.items():
            setattr(instance, key, val)
        instance.save()
        instance.refresh_from_db()
        return instance
