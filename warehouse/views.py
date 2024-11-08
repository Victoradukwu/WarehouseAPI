import math
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from djangorestframework_camel_case.parser import CamelCaseFormParser, CamelCaseMultiPartParser, CamelCaseJSONParser
from drf_spectacular.utils import extend_schema
from rest_framework import status
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


@extend_schema(methods=['post'], request=serializers.ManageUserSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([CamelCaseJSONParser])
def manage_user(request):
    if 'Admin' not in request.user.groups.values_list('name', flat=True):
        return Response({'detail': 'Permission Denied'}, status=403)
    serializer = serializers.ManageUserSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'detail': 'Successful'})


@api_view()
def get_roles(request):
    roles = Group.objects.values('id', 'name')
    return Response(roles)
