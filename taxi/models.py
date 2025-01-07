from datetime import datetime

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


def get_user_directory_path(self, instance, filename: str) -> str:
    return f'profile/{instance.user.username}/{filename}'


class AbstractTaxiUser(models.Model):
    history = HistoricalRecords(inherit=True)
    location = models.ForeignKey(District, on_delete=models.PROTECT, null=True)
    profile_image = models.ImageField(
        'Profile image',
        upload_to=get_user_directory_path,
        null=True,
        blank=False,
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    @property
    def average_rating(self) -> float:
        rates_count = self.rates.count()
        if not rates_count:
            return 0
        return self.rates.aggregate(models.Sum('rate'))['rate__sum'] / rates_count

    @property
    def profile_image_url(self) -> str | None:
        return self.profile_image.url if self.profile_image else None

    def __str__(self):
        return f'f{self.user}'

    class Meta:
        verbose_name='Пользователь'
        abstract=True


class DriverManager(models.Manager):
    def available(self): 
        return self.objects.filter(rides__date_ended__isnull=False
            ).annotate(num_b=Count('b')).filter(num_b__gt=0
            ).filter(current_car_isnull=True).count() > 0
    def free(self):
        return self.objects.all()


class Driver(AbstractTaxiUser):
    objects = DriverManager()

    current_car = models.OneToOneField(
        Car,
        on_delete=models.PROTECT,
        null=True,
    )

    @property
    def if_free(self) -> bool:
        return self.current_car is not None and \
            not self.rides.filter(date_ended__isnull).count()

    class Meta:
        verbose_name_plural = 'Водители'
        verbose_name = 'Водитель'


class Consumer(AbstractTaxiUser):
    class Meta:
        verbose_name_plural = 'Пассажиры'
        verbose_name = 'Пассажир'
 

class Ride(models.Model):
    # Status list
    SEARCHING_DRIVER = 'Searching driver'
    WAITING_DRIVER = 'Wating driver'
    IN_PROGRESS = 'In progress'
    COMPLETED = 'Completed'
    
    # Model fields declaration
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
    def price(self) -> int:
        return 1337

    @property
    def pending_addresses(self):
        return self.addresses.filter(date_ended__isnull=True)
    
    def complete_address(self) -> bool:
        if self.pending_addresses.count():
            address_queue_instance = self.pending_addresses.first()
            address_queue_instance.date_ended = datetime.now()
            address_queue_instance.save()
        else:
            return True
        return False

    @property
    def status(self) -> str:
        if not self.driver:
            return self.SEARCHING_DRIVER
        elif not self.addresses.first().date_ended:
            return self.WAITING_DRIVER
        elif not self.date_ended:
            return self.IN_PROGRESS
        else:
            return self.COMPLETED


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
        null=False,
        blank=False,
        related_name='addresses',
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='rides',
    )
    order = models.PositiveIntegerField('Order', default=0, null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(default=None, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.order + 1}. {self.ride}'

    def save(self, *args, force_insert=False, **kwargs):
        if force_insert or self.order is None:
            self.order = RideAddressesQueue.objects.filter(ride_id=self.ride_id).count()
        super().save(*args, **kwargs)
        if not self.ride.pending_addresses.count():
            self.ride.date_ended = datetime.now()
            self.ride.save()

    class Meta:
        verbose_name_plural = 'Очереди поездок'
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
