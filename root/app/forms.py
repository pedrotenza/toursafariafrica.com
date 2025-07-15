from django import forms
from .models import Booking, Participant

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['nationality', 'age']

ParticipantFormSet = forms.inlineformset_factory(
    Booking,
    Participant,
    form=ParticipantForm,
    extra=1,
    min_num=1,
    validate_min=True
)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['safari', 'date', 'client_name', 'client_email', 'client_phone']