import datetime
import math
import uuid

import django_filters
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.db import transaction
from djangorestframework_camel_case.parser import CamelCaseFormParser, CamelCaseMultiPartParser, CamelCaseJSONParser
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from warehouse import serializers, models, utils, permissions


class PageSizeAndNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        page_resp = super().get_paginated_response(data)
        page_obj = page_resp.data
        num_of_pages = math.ceil(page_obj['count']/self.page_size)
        page_obj['number_of_pages'] = num_of_pages
        return Response(page_obj)


@extend_schema(methods=['POST'], description='This endpoint handles registration', request=serializers.RegisterSerializer)
@api_view(['POST'])
@parser_classes([CamelCaseFormParser, CamelCaseMultiPartParser])
def register(request):
    serializer = serializers.RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user, token = serializer.save()

    data = {"user": user, "access_token": token.key}
    return Response(serializers.UserTokenSerializer(data).data, status=status.HTTP_201_CREATED)


@extend_schema(methods=['post'], request=serializers.LoginSerializer)
@api_view(['POST'])
def login(request):
    wrong_credentials = {"detail": "Wrong credentials."}
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    if data.get('email'):
        user = authenticate(request, email=data['email'], password=data['password'])
    else:
        return Response({'detail': 'Please provide email or phone number.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user:
        return Response(wrong_credentials, status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)

    data = {"user": user, "access_token": token.key}

    return Response(serializers.UserTokenSerializer(data).data, status=status.HTTP_200_OK)


@api_view()
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()

    return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)


@api_view()
def initiate_password_reset(request, email):
    user = models.User.objects.filter(email=email).first()
    if user:
        token = uuid.uuid4().hex
        models.PasswordResetToken.objects.create(user=user, key=token, status='Active')
        utils.send_pw_reset_email(token, user)
        return Response({'detail': 'Please check your email'})
    return Response({'detail': 'User matching email not found'}, status=404)


@api_view()
def password_reset_token_status(request, token):
    try:
        token_obj = models.PasswordResetToken.objects.get(key=token)
    except models.PasswordResetToken.DoesNotExist:
        return Response({'detail': 'Invalid token'})
    return Response({'status': token_obj.status})

@extend_schema(methods=['post'], request=serializers.PasswordResetSerializer)
@api_view(['POST'])
def complete_password_reset(request):
    serializer = serializers.PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer.save(serializer.validated_data)
    return Response({'detail': 'Password reset successful'})


@extend_schema(methods=['post'], request=serializers.PasswordChangeSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = serializers.PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    serializer.save()
    return Response({'detail': 'Password change successful'})


@extend_schema(methods=['post'], request=serializers.ManageUserSerializer, description='The user with "Admin" role uses this endpoint to change activate/deactivate a user and to change the roles assignemd to a user')
@api_view(['POST'])
@permission_classes([permissions.IsWareHouseAdmin])
@parser_classes([CamelCaseJSONParser])
def manage_user(request):
    serializer = serializers.ManageUserSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'detail': 'Successful'})


class UserListView(generics.ListAPIView):
    """
       This endpoint returns a list of users
    """
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return models.User.objects.all()


class UserRetrieveView(generics.RetrieveAPIView):
    """
       This endpoint returns the details of a single user
    """
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return models.User.objects.all()


@extend_schema(description='This endpoint returns a list of available roles in the system. The Admin can then select the roles to assign to users')
@api_view()
def get_roles(request):
    roles = Group.objects.values('id', 'name')
    return Response(roles)


class SupplierListView(generics.ListCreateAPIView):
    """
       get:
       Return a list of supplier objects
       post:
       Create a new supplier object

    """
    permission_classes = [permissions.IsWareHouseManager]
    serializer_class = serializers.SupplierSerializer

    def get_queryset(self):
        return models.Supplier.objects.filter(status=models.ACTIVE)


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
       get:
       Retrieves a single supplier objects
       patch:
       Updates a single supplier objects
       delete:
       Deletes a single supplier objects
    """
    permission_classes = [permissions.IsWareHouseManager]
    serializer_class = serializers.SupplierSerializer
    allowed_methods = ['patch', 'delete', 'get']

    def get_queryset(self):
        return models.Supplier.objects.filter(status=models.ACTIVE)

    def perform_destroy(self, instance):
        instance.status = models.INACTIVE
        instance.save()


class ProductListView(generics.ListCreateAPIView):
    """
       get:
       Return a list of product objects
       post:
       Create a new product object

    """
    permission_classes = [permissions.IsWareHouseManager]
    serializer_class = serializers.ProductSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = utils.ProductFilter

    def get_queryset(self):
        return models.Product.objects.filter(status=models.ACTIVE).all()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
       get:
       Retrieves a single product objects
       patch:
       Updates a single product objects
       delete:
       Deletes a single product objects
    """
    permission_classes = [permissions.IsWareHouseManager]
    serializer_class = serializers.ProductSerializer
    allowed_methods = ['patch', 'delete', 'get']

    def get_queryset(self):
        return models.Product.objects.filter(status=models.ACTIVE).all()

    def perform_destroy(self, instance):
        instance.status = models.INACTIVE
        instance.save()


def create_product_movement(product_id, quantity, movement_type, user_id, stock_before, invoice_id=None):
    models.StockMovement.objects.create(
        date=datetime.datetime.now(),
        product_id=product_id,
        quantity=quantity,
        movement_type=movement_type,
        user_id=user_id,
        invoice_id=invoice_id,
        stock_before=stock_before
    )


@transaction.atomic
def update_stock(product, change_type, quantity, user, invoice_id=None):
    if change_type not in ['Decrease', 'Increase']:
        raise ValueError('Change type must be either "Decrease" or "Increase"')

    stock_before = product.stock_value
    if change_type == 'Decrease' and product.stock_value < float(quantity):
        raise ValueError('Insufficient stock')
    if change_type == 'Decrease':
        product.stock_value -= float(quantity)
        product.save()
        create_product_movement(product.id, float(quantity), models.StockMovement.DECREASE, user.id, stock_before, invoice_id)
    else:
        product.stock_value += float(quantity)
        product.save()
        create_product_movement(product.id, float(quantity), models.StockMovement.INCREASE, user.id, stock_before, invoice_id)
    product.refresh_from_db()
    return product


@transaction.atomic
def supply_invoice_items(invoice, user):
    invoice_products = models.InvoiceProduct.objects.filter(invoice=invoice)
    for inv in invoice_products:
        product = models.Product.objects.get(id=inv.product_id)
        update_stock(product, 'Decrease', inv.quantity, user, invoice.id)
    return


@extend_schema(description='This endpoint is called to update the product stock value. Change_type is either `Increase` or `Decrease` Only the "Warehouse Manager" has authorization for this. Whenever there is a supply from a supplier, the Warehouse Manager uses this endpoint to update the records.')
@api_view()
@permission_classes([permissions.IsWareHouseManager])
@parser_classes([CamelCaseJSONParser])
def stock_update(request, product_id, quantity, change_type):
    if change_type not in ['Increase','Decrease']:
        raise ValueError('Change type must be either "Increase" or "Decrease"')
    product = models.Product.objects.get(id=product_id)
    updated_product = update_stock(product, change_type, quantity, request.user)
    return Response(serializers.ProductSerializer(updated_product).data)


class StockMovementListView(generics.ListAPIView):
    """
       This endpoint returns a list of stock_movement objects. The records returned here are generated when sales are made or when the warehouse is restocked
    """
    serializer_class = serializers.StockMovementSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = utils.StockMovementFilter

    def get_queryset(self):
        return models.StockMovement.objects.all()


@extend_schema(methods=['post'], request=serializers.InvoiceCreateSerializer)
@api_view(['POST'])
@permission_classes([permissions.IsCashier])
@parser_classes([CamelCaseJSONParser])
def create_invoice(request):
    serializer = serializers.InvoiceCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    invoice = serializer.save()
    return Response(serializers.InvoiceSerializer(invoice).data)


@api_view()
def list_invoices(request):
    invoices = models.Invoice.objects.filter(status=models.ACTIVE)
    return Response(serializers.InvoiceSerializer(invoices, many=True).data)


@extend_schema(description='This endpoint returns the details of a single invoice')
@api_view()
def retrieve_invoice(request, pk):
    invoice = models.Invoice.objects.filter(status=models.ACTIVE).get(id=pk)
    return Response(serializers.InvoiceSerializer(invoice).data)


@extend_schema(methods=['patch'], request=serializers.InvoiceUpdateSerializer)
@api_view(['PATCH'])
@permission_classes([permissions.IsCashier])
@parser_classes([CamelCaseJSONParser])
def update_invoice(request, pk):
    instance = models.Invoice.objects.filter(status=models.ACTIVE).get(id=pk)
    if instance.invoice_status != models.Invoice.PENDING:
        raise ValueError('You can only update an invoice before payment')
    serializer = serializers.InvoiceUpdateSerializer(data=request.data, context={'request': request, 'pk': pk})
    serializer.is_valid(raise_exception=True)
    invoice = serializer.save()
    return Response(serializers.InvoiceSerializer(invoice).data)


@api_view(['DELETE'])
@permission_classes([permissions.IsCashier])
def delete_invoice(request, pk):
    invoice = models.Invoice.objects.filter(status=models.ACTIVE).get(id=pk)
    invoice.status = models.INACTIVE
    invoice.save()
    return Response(status=204)


@extend_schema(description='This endpoint is called to mark an invoice as `Paid`. Only the `Cashier` has this authorization')
@api_view()
@permission_classes([permissions.IsCashier])
def pay_invoice(request, pk):
    invoice = models.Invoice.objects.filter(status=models.ACTIVE).get(id=pk)
    invoice.invoice_status = models.Invoice.PAID
    invoice.date_paid = datetime.datetime.now()
    invoice.save()
    return Response({'detail': 'Invoice paid'})


@extend_schema(description='This endpoint is called to indicated that the items on the specified invoice have been delivered to the buyer. Only the `Salesperson` has this authorization')
@api_view()
@permission_classes([permissions.IsSalesperson])
def supply_invoice(request, pk):
    invoice = models.Invoice.objects.filter(status=models.ACTIVE).get(id=pk)
    if invoice.invoice_status != models.Invoice.PAID:
        raise ValueError('This invoice has not been paid yet')
    supply_invoice_items(invoice, request.user)
    invoice.invoice_status = models.Invoice.DELIVERED
    invoice.date_supplied = datetime.datetime.now()
    invoice.save()
    return Response({'detail': 'Invoice supplied'})
