import pytz
import datetime

from django import template
from django.conf import settings

from taxi.models import AbstractTaxiUser, Consumer, Driver, Address

register = template.Library()

@register.filter
def user_filter(user: AbstractTaxiUser):
    user_type = None
    if not user:
        return 'Не задан'
    if Consumer.objects.filter(user=user.user):
        user_type = 'Пассажир'
    elif Driver.objects.filter(user=user.user):
        user_type = 'Водитель'
    else:
        raise ValueError(__name__, 'user is not registered as Driver or Consumer instance')
 
    return f'{user_type}: {user.user.first_name} {user.user.first_name} рейтинг: {user.average_rating}'


@register.filter
def shorter_address_filter(address: Address): 
    return f'{address.street.name} {address.name}'


@register.simple_tag(takes_context=True)
def current_time(context, format_string):
    timezone = settings.TIME_ZONE
    if hasattr(context, 'user_timezone'):
        timezone = context['user_timezone']
    now = datetime.datetime.now().replace(tzinfo=pytz.timezone(timezone))
    return now.strftime(format_string)
