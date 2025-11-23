from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, CustomSetPasswordForm
urlpatterns = [
   path('register/',views.register,name='register'), 
   path('login/',views.login,name="login"), 
   path('logout/', views.logout, name='logout'),
   path('profile/', views.profile, name='profile'),
   path('auth/google/', views.google_login, name='google_login'),
   path('auth/google/callback/', views.google_callback, name='google_callback'),
   path('oauth-test/', views.google_oauth_test, name='oauth_test'),
   # Password reset URLs
   path('password-reset/', CustomPasswordResetView.as_view(
       template_name='users/password_reset_form.html',
       email_template_name='users/password_reset_email.html',
   ), name='password_reset'),
   path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
       template_name='users/password_reset_done.html'
   ), name='password_reset_done'),
   path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
       template_name='users/password_reset_confirm.html',
       form_class=CustomSetPasswordForm
   ), name='password_reset_confirm'),
   path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
       template_name='users/password_reset_complete.html'
   ), name='password_reset_complete'),
]
 