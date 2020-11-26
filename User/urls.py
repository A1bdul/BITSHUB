from django.urls import path, include
from User import views

urlpatterns = [
    path('account/signup', views.SignUp.as_view(), name='signup'),
    path('set-password/<uidb64>/<token>', views.SetPasswordView.as_view(), name='set-password'),
    path('account/login', views.LoginView.as_view(), name='login'),
    path('activate/<uidb64>/<token>', views.ActiveAccountView.as_view(), name='activate'),
    path('request/reset-password/', views.ResetPasswordView.as_view(), name='reset'),
    path('oauth/', include('social_django.urls', namespace='social'),),
    path('logout/', views.LogoutView.as_view(), name='logout')
]