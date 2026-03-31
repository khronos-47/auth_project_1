from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Role, Permission, UserRole, RolePermission, BlacklistedToken
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserUpdateSerializer,
    RoleSerializer, PermissionSerializer, UserRoleSerializer, RolePermissionSerializer
)
from .permissions import HasPermission

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({'detail': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'detail': 'Учетная запись отключена'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Refresh token обязателен'}, status=status.HTTP_400_BAD_REQUEST)
            # Добавляем токен в чёрный список
            BlacklistedToken.objects.create(token=refresh_token, user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Разрешаем обновлять только определённые поля через отдельный сериализатор
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    def delete(self, request, *args, **kwargs):
        # Мягкое удаление
        user = request.user
        user.is_active = False
        user.save()
        # Удаляем все refresh-токены пользователя из чёрного списка (хотя они уже неактивны)
        BlacklistedToken.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Административные views (требуют manage_roles)
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'manage_roles'

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'manage_roles'

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'manage_roles'

    def get_queryset(self):
        # Фильтрация по user_id, если передан в URL
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'manage_roles'

    def get_queryset(self):
        role_id = self.request.query_params.get('role_id')
        if role_id:
            return self.queryset.filter(role_id=role_id)
        return self.queryset

# Mock-объекты (items)
class MockItemView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'view_item'  # для GET

    def get(self, request):
        # Возвращаем список вымышленных объектов
        items = [
            {"id": 1, "name": "Товар 1"},
            {"id": 2, "name": "Товар 2"},
        ]
        return Response(items)

    def post(self, request):
        # Проверка права add_item
        if not request.user.has_perm('add_item'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        # Мок-создание
        return Response({"id": 3, "name": "Новый товар"}, status=status.HTTP_201_CREATED)

class MockItemDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'view_item'  # для GET

    def get(self, request, pk):
        # Проверка права view_item
        if not request.user.has_perm('view_item'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return Response({"id": pk, "name": f"Товар {pk}"})

    def put(self, request, pk):
        if not request.user.has_perm('change_item'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return Response({"id": pk, "name": request.data.get('name', f"Обновленный товар {pk}")})

    def delete(self, request, pk):
        if not request.user.has_perm('delete_item'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)