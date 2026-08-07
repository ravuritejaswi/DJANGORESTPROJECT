from django.urls import path
from .views import LoginAPIView, ProfileListAPIView, RegisterAPIView, ProfileAPIView, ChangePasswordAPIView, LogoutAPIView, ProfileCRUDAPIView
from .views import RestoreProfileAPIView
urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("logout/",LogoutAPIView.as_view(),name="logout"),
    path("profile-crud/", ProfileCRUDAPIView.as_view(), name="profile-crud"),
    path("profiles/", ProfileListAPIView.as_view(), name="profiles"),
    path("profile-restore/",RestoreProfileAPIView.as_view(),name="profile_restore",),
]

