from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from auth_app.models import Role, Permission, UserRole, RolePermission

User = get_user_model()

class Command(BaseCommand):
    help = 'Загружает тестовые данные для демонстрации'

    def handle(self, *args, **options):
        # Создаём права
        permissions = [
            ('view_user', 'Просмотр пользователей'),
            ('edit_user', 'Редактирование пользователей'),
            ('delete_user', 'Удаление пользователей'),
            ('manage_roles', 'Управление ролями'),
            ('view_role', 'Просмотр ролей'),
            ('edit_role', 'Редактирование ролей'),
            ('view_item', 'Просмотр товаров'),
            ('add_item', 'Добавление товаров'),
            ('change_item', 'Изменение товаров'),
            ('delete_item', 'Удаление товаров'),
        ]
        for codename, name in permissions:
            Permission.objects.get_or_create(codename=codename, defaults={'name': name})

        # Создаём роли
        admin_role, _ = Role.objects.get_or_create(name='admin', defaults={'description': 'Администратор'})
        editor_role, _ = Role.objects.get_or_create(name='editor', defaults={'description': 'Редактор'})
        viewer_role, _ = Role.objects.get_or_create(name='viewer', defaults={'description': 'Наблюдатель'})

        # Назначаем права ролям
        # Admin — все права
        all_perms = Permission.objects.all()
        for perm in all_perms:
            RolePermission.objects.get_or_create(role=admin_role, permission=perm)

        # Editor — права на пользователей (просмотр и редактирование) и на товары (все кроме удаления)
        editor_perms_codenames = ['view_user', 'edit_user', 'view_item', 'add_item', 'change_item']
        for codename in editor_perms_codenames:
            perm = Permission.objects.get(codename=codename)
            RolePermission.objects.get_or_create(role=editor_role, permission=perm)

        # Viewer — только просмотр пользователей и товаров
        viewer_perms_codenames = ['view_user', 'view_item']
        for codename in viewer_perms_codenames:
            perm = Permission.objects.get(codename=codename)
            RolePermission.objects.get_or_create(role=viewer_role, permission=perm)

        # Создаём пользователей
        admin_user, _ = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if admin_user.password != 'pbkdf2_sha256$...' or not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.save()
        # Назначаем роль админа (хотя суперпользователь и так имеет все права, но для единообразия)
        UserRole.objects.get_or_create(user=admin_user, role=admin_role)

        editor_user, _ = User.objects.get_or_create(
            email='editor@example.com',
            defaults={'first_name': 'Editor', 'last_name': 'User', 'is_active': True}
        )
        editor_user.set_password('editor123')
        editor_user.save()
        UserRole.objects.get_or_create(user=editor_user, role=editor_role)

        viewer_user, _ = User.objects.get_or_create(
            email='viewer@example.com',
            defaults={'first_name': 'Viewer', 'last_name': 'User', 'is_active': True}
        )
        viewer_user.set_password('viewer123')
        viewer_user.save()
        UserRole.objects.get_or_create(user=viewer_user, role=viewer_role)

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены'))