from django import forms
from .models import Booking, Participant

# Formulario para los participantes
class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['nationality', 'age']

# Formset para manejar varios participantes
ParticipantFormSet = forms.inlineformset_factory(
    Booking,
    Participant,
    form=ParticipantForm,
    extra=1,
    min_num=1,
    validate_min=True
)

# Formulario para Booking
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'safari',
            'date',
            'client_name',
            'client_email',
            'client_phone_prefix',
            'client_phone_number',
        ]

    # Limpiar el número de teléfono para eliminar el 0 inicial
    def clean_client_phone_number(self):
        phone = self.cleaned_data.get('client_phone_number', '')
        if phone.startswith('0'):
            phone = phone[1:]  # eliminar el cero inicial
        return phone
