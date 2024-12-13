import datetime

from django.db import models
from django.conf import settings
from django.core import validators
from simple_history.models import HistoricalRecords


class Car(models.Model):
    class CarComfortClass(models.TextChoices):
        COMFORT_PLUS = 'comfort_plus', 'Comfort Plus'
        BUSINESS = 'business', 'Business'
        TOGETHER = 'together', 'Together'
        COMFORT = 'comfort', 'Comfort'
        ECONOM = 'econom', 'Econom'

    number = models.CharField('Car Number', max_length=10, primary_key=True)
    color = models.CharField('Color', max_length=63, blank=False, null=False)
    make = models.CharField('Make', max_length=100, blank=False, null=False)
    series = models.CharField('Series', max_length=100, blank=False, null=False)

    is_ready = models.BooleanField('Ready to use', default=True, blank=False, null=False)
    comfort_class = models.CharField( 'Comfort class', max_length=50, choices=CarComfortClass.choices) 

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Машины'

    def __str__(self):
        return f'{self.number}: {self.color} {self.make} {self.series}'


class City(models.Model):
    name = models.CharField('City', max_length=511, primary_key=True)

    class Meta:
        verbose_name_plural = 'Города'

    def __str__(self) -> str:
        return f'{self.name}'


class District(models.Model):
    city = models.ForeignKey(
        City,
        null=False,
        blank=False,
        related_name='districts',
        on_delete=models.CASCADE
    )
    name = models.CharField('District', max_length=511, null=False, blank=False)

    def __str__(self) -> str:
        return f'{self.city} {self.name}'

    class Meta:
        verbose_name_plural = 'Районы'
        unique_together = (('city', 'name'),)
        ordering = 'city name'.split()


class Street(models.Model):
    district = models.ForeignKey(
        District,
        null=False,
        blank=False,
        related_name='streets',
        on_delete=models.CASCADE
    )
    name = models.CharField('Street name', max_length=511, null=False, blank=False)

    def __str__(self) -> str:
        return f'{self.district} {self.name}'

    class Meta:  
        verbose_name_plural = 'Улицы'
        unique_together = (('district', 'name'),)
        ordering = 'district name'.split()


class Address(models.Model):
    street = models.ForeignKey(
        Street,
        null=False,
        blank=False,
        related_name='addresses',
        on_delete=models.CASCADE,
    )
    name = models.CharField('Address name', max_length=10, null=False, blank=False)

    def __str__(self) -> str:
        return f'{self.street} {self.name}'

    class Meta:
        verbose_name_plural = 'Адреса'
        unique_together = (('street', 'name'),)
        ordering = 'street name'.split()


class DriverManager(models.Manager):
    def available(self): 
        return self.objects.filter(rides__date_ended__isnull=False).annotate(num_b=Count('b')).filter(num_b__gt=0).filter(current_car_isnull=True).count() > 0
    def free(self):
        return Q()


class Driver(models.Model):
    objects = DriverManager()
    history = HistoricalRecords()
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    current_car = models.OneToOneField(
        Car,
        on_delete=models.PROTECT,
        null=True,
    )

    location = models.ForeignKey(District, on_delete=models.PROTECT, null=True)

    @property
    def if_free(self) -> bool:
        return self.current_car is not None and \
            not self.rides.filter(date_ended__isnull).count()

    @property
    def average_rating(self) -> float:
        return self.rates.aggregate(models.Sum('rate'))['rate__sum'] / self.rates.count()

    class Meta:
        verbose_name_plural = 'Водители'

    def __str__(self):
        return f'Driver: {self.user}'
        

class Consumer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    location = models.ForeignKey(District, on_delete=models.PROTECT, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Пассажиры'

    def __str__(self):
        return f'Consumer: {self.user}'
    

class Ride(models.Model):
    consumer = models.ForeignKey(
        Consumer,
        on_delete=models.PROTECT,
        related_name='rides'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name='rides',
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(default=None, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.id} {self.driver} {self.consumer} Price: {self.price} at: {self.date_created}'

    class Meta:
        verbose_name_plural = 'Поездки'
        unique_together = (('consumer', 'driver', 'date_created'),)
        ordering = 'driver date_created '.split()
 
    @property
    def price(self):
        pass

    @property
    def status(self):
        pass


class Rate(models.Model):
    ride = models.ForeignKey(
        Ride,
        on_delete=models.PROTECT,
    )
    comment = models.TextField('Comment', blank=False, null=False)
    rate = models.PositiveIntegerField('Rate',  validators=(validators.MaxValueValidator(5),))
    date_created = models.DateTimeField('Date created', auto_now_add=True)

    def __str__(self):
        return f'{self.target} Rate: {self.rate} Author: {self.author}'

    class Meta:
        abstract=True
        verbose_name_plural = 'Оценки'
        ordering = 'target date_created'.split()


class DriverRate(Rate):
    author = models.ForeignKey(
        Consumer,
        on_delete=models.PROTECT,
        related_name='rates_authored'
    )
    target = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name='rates'
    )

    class Meta:
        verbose_name_plural = 'Оценки водителей'


class ConsumerRate(Rate):
    target = models.ForeignKey(
        Consumer,
        on_delete=models.PROTECT,
        related_name='rates'
    )
    author = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name='rates_authored'
    )
    class Meta:
        verbose_name_plural = 'Оценки пассажиров'


class RideAddressesQueue(models.Model):
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        blank=False,
        related_name='adresses',
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        blank=False,
        related_name='rides',
    )
    order = models.PositiveIntegerField('Order', default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(default=None, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.order + 1}. {self.ride}'

    def save(self, *args, force_insert=False, **kwargs):
        if self.date_ended and self.date_ended < self.date_created:
            raise ValueError(__name__ + 'date_created date_created > date_endede')
        if force_insert:
            default_order = SubjectScheduleItemQueue.objects.filter(subject_item=self.subject_item).count()
            self.order = default_order
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Истории путей'
        unique_together = (('ride', 'address'),)
        ordering = 'order date_ended date_created'.split()


def on_delete_queue(instance, **kwargs):
    for queue_record in RideAddressesQueue.objects.filter(ride = instance.ride, order__gt = instance.order):
        queue_record.order -= 1
        queue_record.save(force_update=True)
    

models.signals.post_delete.connect(
    on_delete_queue,
    sender=RideAddressesQueue,
    dispatch_uid='on_delete_queue'
)
