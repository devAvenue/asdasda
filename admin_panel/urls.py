from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('add-user/', views.AddUserView.as_view(), name='add_user'),
    path('mammoths/', views.MyMammothsView.as_view(), name='mammoths'),
    path('users/', views.AllUsersView.as_view(), name='users'),
    path('profits/', views.AllProfitsView.as_view(), name='profits'),
    path('user/<int:user_id>/', views.GetUserView.as_view(), name='get_user'),
    path('wallet/<str:address>/', views.WalletView.as_view(), name='get_wallet'),
    path('user/verify_kyc/', views.KYCVerify.as_view(), name='verify_kyc'),
    path('user/update_balance/', views.UpdateBalance.as_view(), name='update_balance'),
    path('user/min_deposit/', views.MinDeposit.as_view(), name='min_deposit'),
    path('user/referral_bonus/', views.ReferralBonus.as_view(), name='referral_bonus'),
    path('user/bind-user/', views.BindUser.as_view(), name='bind_user'),
    path('user/ban/', views.BanUser.as_view(), name='ban'),
    path('user/set-worker/', views.SetWorker.as_view(), name='set_worker'),
    path('user/add-bot-token/', views.AddBotToken.as_view(), name='add_bot_token'),
    path('user/add-support-token/', views.AddChatToken.as_view(), name='add_chat_token'),
    path('user/change-notification/', views.CheckNotification.as_view(), name='check_notification'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
