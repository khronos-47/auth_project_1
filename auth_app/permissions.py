from rest_framework.permissions import BasePermission

class HasPermission(BasePermission):
    """
    Проверяет, есть ли у пользователя указанное право (codename).
    """
    def has_permission(self, request, view):
        # Получаем требуемое право из атрибута view
        required = getattr(view, 'permission_required', None)
        if not required:
            return True  # Если право не задано, доступ разрешён

        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Если пользователь суперпользователь
        if user.is_superuser:
            return True

        # Проверяем наличие права через метод модели
        return user.has_perm(required)