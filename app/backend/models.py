import uuid
from django.contrib.auth.models import (
	AbstractBaseUser, PermissionsMixin, UserManager
)
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, 
                                unique=True, verbose_name="ФИО пользователя")
    email = models.CharField(max_length=300, blank=True, null=True)
    telegram_username = models.CharField(
        max_length=255, unique=True, verbose_name="телеграм ник")
    telegram_id = models.CharField(
        max_length=255, unique=True, verbose_name="телеграм id"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Вход в админ панель")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['telegram_username']


class Reminder(models.Model):
    user_message_id = models.CharField(max_length=255, verbose_name="телеграм id для reply_to")
    message_text = models.TextField(verbose_name="Привет, ты просил напомнить что...")
    time_to_remind = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='reminder_user', null=True)


class Poll(models.Model):
    title = models.CharField(max_length=300, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name='poll_choices')
    choice_text = models.CharField(max_length=255, verbose_name='Вопрос')
    text_from_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PossibleVote(models.Model):
    text = models.CharField(max_length=300, verbose_name="Возможный ответ")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="choice_p_vote")


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True)
    choice_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)