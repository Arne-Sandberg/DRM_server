from rest_framework import permissions
from rest_framework.permissions import BasePermission


class CasePermission(BasePermission):
    message = 'Changing other\'s cases is not allowed.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or \
                request.method != 'DELETE' and request.user in obj.in_party:
            return True
        return False


class StagePermission(BasePermission):
    message = 'Changing other\'s case\'s stages is not allowed.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or \
                request.user.is_judge or \
                obj.owner == request.user:
            return True
        return False


class NotificationPermission(BasePermission):
    message = 'Manipulations with others notifications is not allowed.'

    def has_permission(self, request, view):
        if request.method == 'POST':
            # only admin is allowed to create notifications
            return request.user.is_admin
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user_to


class UserPermission(BasePermission):
    message = 'Manipulations with users is not allowed.'

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or \
               request.user == obj.user


class UserInfoPermission(BasePermission):
    message = 'Manipulations with user infos is not allowed.'

    def has_permission(self, request, view):
        if request.method == 'POST':
            # only admin is allowed to create notifications
            return request.user.is_admin
        return True

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or \
               request.user == obj.user
