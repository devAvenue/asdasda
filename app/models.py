from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField

User = get_user_model()


class Message(models.Model):
    username = models.CharField(max_length=255)
    room = models.CharField(max_length=255)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
        #models.IntegerField()
        
class Trader(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=100, null=True)
    telegram_id = models.BigIntegerField(null=True)
    referral_id = models.CharField(max_length=100, null=True)
    min_deposit = models.CharField(max_length=1000, null=True)
    referral_bonus = models.IntegerField()
    kyc_status = models.CharField(max_length=100, null=True)
    terms_text = RichTextUploadingField(null=True)
    bot_token = models.CharField(max_length=500, null=True)
    chat_token = models.CharField(max_length=500, null=True)
    is_worker = models.BooleanField()

    def __str__(self):
        return self.user.username


class Referral(models.Model):
    referrer = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='referral')
    referred = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='referrals')

    class Meta:
        unique_together = ('referred',)


def user_directory_path(instance, filename):
    return 'documents/user_{0}/{1}'.format(instance.user.id, filename)


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to=user_directory_path)

    def __str__(self):
        return self.document


class Visits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField()
    ip = models.GenericIPAddressField()

    def __str__(self):
        return self.user.username


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    wif = models.TextField()
    seed = models.TextField(null=True)
    balance = models.FloatField(null=True)
    name = models.TextField()

    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    currency = models.CharField(max_length=5)
    method = models.CharField(max_length=60)
    status = models.CharField(max_length=60)
    date = models.DateTimeField()

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=True)
    status = models.BooleanField(null=True)

    def __str__(self):
        return self.user.username


class Profit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    worker = models.ForeignKey(Trader, on_delete=models.CASCADE, null=True)
    txid = models.CharField(max_length=500)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField()

    def __str__(self):
        return self.user.username


class Statistic(models.Model):
    new_users = models.IntegerField()
    regular_users = models.IntegerField()
    transaction = models.IntegerField()
    visits = models.IntegerField()
    processing_time = models.IntegerField()
    top_pair = models.CharField(max_length=100)
    date = models.DateTimeField()

    def __str__(self):
        return self.date
