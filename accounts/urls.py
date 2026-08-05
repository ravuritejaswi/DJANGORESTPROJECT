from django.urls import path
from .views import LoginAPIView, RegisterAPIView, ProfileAPIView, ChangePasswordAPIView, LogoutAPIView
urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("logout/",LogoutAPIView.as_view(),name="logout"),
]

