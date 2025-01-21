from django import forms
from taxi.models import Rate, ConsumerRate, DriverRate, Consumer, Driver, Ride


class AbstractRateForm(forms.ModelForm):
    ride = forms.ModelChoiceField(queryset=Ride.objects.non_available())

    def clean_target(self):
        raise RuntimeError(__name__, 'Not defined')

    def clean_author(self):
        raise RuntimeError(__name__, 'Not defined')

    def get_ride(self) -> Ride:
        if self.cleaned_data['ride']:
            return self.cleaned_data['ride']
        raise ValueError(__name__, 'Ride is not defined')

    def get_consumer(self) -> Consumer: 
        return self.get_ride().consumer

    def get_driver(self) -> Driver:
        ride = self.get_ride()
        if hasattr('consumer', ride):
            return ride.driver
        raise ValueError(__name__, 'Ride driver is not defined.')

    class Meta:
        model = Rate
        fields = 'ride comment rate'.split()
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class DriverRateForm(forms.ModelForm):
#   def clean_target(self):
#       return self.get_driver()

#   def clean_author(self):
#       return self.get_consumer()

    class Meta:
        model = DriverRate
        fields = 'ride comment rate'.split()
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class ConsumerRateForm(forms.ModelForm):
#   def clean_target(self):
#       return self.get_consumer()

#   def clean_author(self):
#       return self.get_driver()

    class Meta:
        model = ConsumerRate
        fields = 'ride comment rate'.split()
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }
