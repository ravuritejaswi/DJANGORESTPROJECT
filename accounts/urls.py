from django.urls import path
from .views import LoginAPIView, ProfileListAPIView, RegisterAPIView, ProfileAPIView, ChangePasswordAPIView, LogoutAPIView, ProfileCRUDAPIView, NotificationListAPIView, NotificationReadAPIView, NotificationReadAllAPIView
from .views import RestoreProfileAPIView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("token/refresh/",TokenRefreshView.as_view(),name="token-refresh",),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("logout/",LogoutAPIView.as_view(),name="logout"),
    path("profile-crud/", ProfileCRUDAPIView.as_view(), name="profile-crud"),
    path("profiles/", ProfileListAPIView.as_view(), name="profiles"),
    path("profile-restore/",RestoreProfileAPIView.as_view(),name="profile_restore",),
]

