from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Role, Permission, UserRole, RolePermission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'patronymic', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at')

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'patronymic')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic')

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'description')

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'codename', 'name')

class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True
    )

    class Meta:
        model = UserRole
        fields = ('id', 'user', 'role', 'role_id', 'assigned_at')
        read_only_fields = ('id', 'user', 'assigned_at')

class RolePermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), source='permission', write_only=True
    )

    class Meta:
        model = RolePermission
        fields = ('id', 'role', 'permission', 'permission_id', 'granted_at')
        read_only_fields = ('id', 'role', 'granted_at')