from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'permissions', views.PermissionViewSet)
router.register(r'user-roles', views.UserRoleViewSet)
router.register(r'role-permissions', views.RolePermissionViewSet)

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),

    path('admin/', include(router.urls)),

    path('items/', views.MockItemView.as_view(), name='item-list'),
    path('items/<int:pk>/', views.MockItemDetailView.as_view(), name='item-detail'),
]