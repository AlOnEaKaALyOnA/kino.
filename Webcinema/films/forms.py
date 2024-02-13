from django import forms

class ReservationForm(forms.Form):
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='Номер телефона')
    selected_seats = forms.CharField(widget=forms.HiddenInput())