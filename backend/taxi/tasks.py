from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_per_minute_newsletter():
    send_mail(
        'Проверка связи',
        'Получай!',
        'vasylyevkirill@yandex.com',
        ['admin@admin.ru'],
        fail_silently=False,
    )


@shared_task
def send_new_year_newsletter():
    User = settings.AUTH_USER_MODEL
    users = User.objects.all()
    for user in users:
        send_mail(
            'С новым годом!',
            f'Наш сервси поздравляет вас с новым 2025 таксистским годом, {user.nickname}!',
            'vasylyevkirill@yandex.com',
            [user.email],
            fail_silently=False,
        )
