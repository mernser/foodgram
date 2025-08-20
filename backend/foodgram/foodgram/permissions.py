from rest_framework import permissions


class UserDetailPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user and request.user.is_authenticated
        return True


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class OwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
