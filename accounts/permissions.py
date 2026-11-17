from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
  def has_permission(self, request, view):
    return (request.user and request.user.is_authenticated and(request.user.role == "admin" or request.method in SAFE_METHODS))

class IsAdminOrOwnStudentProfile(BasePermission):
  def has_object_permission(self, request, view, obj):
    if request.user.role == "admin":
      return True

    if request.user.role == "student":
      return obj.user_id == request.user.id
    return False