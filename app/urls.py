from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('support/', views.suppoort, name='suppoort'),
    path('support/<str:room_name>/', views.room, name='room'),
    path('exchange/', views.exchange, name='exchange'),
    path('esupport/', views.supp.as_view(), name='esupport'),
    path('terms/', views.terms, name='terms'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('deposit', views.DepositView.as_view(), name='deposit'),
    path('withdraw', views.WithdrawView.as_view(), name='withdraw'),
    path('transaction/', views.TransactionView.as_view(), name='transaction'),
    path('user/kyc/', views.VerificationView.as_view(), name='verification'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('ref/<str:ref>/', views.set_referral, name='set_referral'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
