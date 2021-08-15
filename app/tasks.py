import requests
import random
from time import sleep
from datetime import datetime
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from exchange import settings
from celery import shared_task
from .models import *
from .bot import BotAlert, send_profit_to_channel


@shared_task
def new_statistic():
    new_users = random.randint(15, 30)
    top_pair = ['ETH/BTC', 'LTC/BTC', 'BCH/BTC', 'DASH/BTC', 'LTC/ETH', 'BCH/ETH', 'BTC/ETH', 'DASH/ETH', 'BTC/USDT',
                'ETH/USDT', 'DASH/USDT', 'LTC/USDT', 'BCH/USDT']
    Statistic.objects.create(
        new_users=new_users,
        regular_users=100 - new_users,
        transaction=round(random.randint(1700, 4500) / 100) * 100,
        visits=round(random.randint(25000, 45000) / 50) * 50,
        processing_time=random.randint(8, 20),
        top_pair=random.choice(top_pair),
        date=datetime.now()
    )


@shared_task
def check_address():
    wallets = Wallet.objects.filter(Q(name='btc') | Q(name='ltc') | Q(name='dash'))
    for wallet in wallets:
        sleep(1)
        req = requests.get(f'https://chain.so/api/v2/get_tx_received/{wallet.name}/{wallet.address}')
        if len(req.json()['data']['txs']) == 0:
            continue
        txs = req.json()['data']['txs'][-1]
        profit = Profit.objects.filter(txid=txs["txid"]).first()
        if profit:
            continue
        else:
            add_new_profit(wallet, txs['txid'], round(float(txs['value']), 4), wallet.name)


@shared_task
def check_eth():
    wallets = Wallet.objects.filter(name='eth').all()
    for wallet in wallets:
        sleep(1)
        req = requests.get(
            'http://api.etherscan.io/api?module=account&action=txlist' +
            f'&address={wallet.address}&sort=asc&apikey={settings.ETHERSCAN_API}'
        )
        if len(req.json()['result']) == 0:
            continue
        result = req.json()['result']
        for i in result:
            if i['to'] != wallet.address:
                result.remove(i)
        txs = result[-1]
        profit = Profit.objects.filter(txid=txs["hash"]).first()
        if profit:
            continue
        else:
            add_new_profit(wallet, txs['hash'], round(float(txs['value']) / 1000000000000000000, 4), 'eth')


@shared_task
def check_usdt():
    wallets = Wallet.objects.filter(name='usdt').all()
    for wallet in wallets:
        sleep(1)
        req = requests.get(
            'https://api.etherscan.io/api?module=account&action=tokentx' +
            f'&address={wallet.address}&sort=asc&apikey={settings.ETHERSCAN_API}'
        )
        if len(req.json()['result']) == 0:
            continue
        result = req.json()['result']
        for i in result:
            if i['to'] != wallet.address:
                result.remove(i)
        txs = result[-1]
        profit = Profit.objects.filter(txid=txs["hash"]).first()
        if profit:
            continue
        else:
            add_new_profit(wallet, txs['hash'], round(float(txs['value']) / 1000000, 2), 'usdt')


@shared_task
def check_bch():
    wallets = Wallet.objects.filter(name='bch').all()
    for wallet in wallets:
        sleep(1)
        req = requests.get(
            f'https://rest1.biggestfan.net/v2/address/transactions/bitcoincash:{wallet.address}'
        )
        if len(req.json()['txs']) == 0:
            continue
        txs = req.json()['txs']
        for i in txs:
            if i['vin'][0]['cashAddress'] != f'bitcoincash:{wallet.address}':
                txs.remove(i)
        txs = txs[-1]
        profit = Profit.objects.filter(txid=txs['vin'][0]['txid']).first()
        if profit:
            continue
        else:
            add_new_profit(wallet, txs['vin'][0]['txid'], round(txs['vin'][0]['valueSat'], 4), 'bch')


def add_new_profit(wallet, txid, amount, currency):
    user = Trader.objects.filter(user_id=wallet.user_id).first()
    worker = Referral.objects.filter(referred=user).first()
    if worker:
        worker = worker.referrer
        send_profit = BotAlert(worker.user, worker.bot_token)
        send_profit.send_profit(txid, amount, currency)
    else:
        worker = None
    send_profit_to_channel(worker, amount, currency)
    new_profit = Profit(
        user=user.user,
        worker=worker,
        txid=txid,
        wallet=wallet,
        amount=amount,
        date=datetime.now(tz=timezone.utc)
    )
    new_profit.save()
    add_new_transaction(wallet, amount, currency)


def add_new_transaction(wallet, amount, currency):
    wallet = Wallet.objects.filter(
        address=wallet.address
    ).filter(
        name=currency
    ).first()
    if wallet:
        wallet.balance += amount
        new_transaction = Transaction(
            user=wallet.user,
            amount=amount,
            currency=currency,
            method='Deposit',
            status='Successfully',
            date=datetime.now(tz=timezone.utc)
        )
        new_transaction.save()
        wallet.save()



