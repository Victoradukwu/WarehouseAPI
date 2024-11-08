from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsWareHouseAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return request.method in SAFE_METHODS or user.is_authenticated and 'Admin' in user.groups.values_list('name', flat=True)


class IsWareHouseManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return request.method in SAFE_METHODS or user.is_authenticated and 'Warehouse Manager' in user.groups.values_list('name', flat=True)


class IsSalesperson(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return request.method in SAFE_METHODS or user.is_authenticated and 'Salesperson' in user.groups.values_list('name', flat=True)

class IsCashier(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return request.method in SAFE_METHODS or user.is_authenticated and 'Cashier' in user.groups.values_list(
            'name', flat=True)
