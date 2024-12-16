from django import forms

class PublicKeyForm(forms.Form):
    public_key = forms.CharField(
        label='Публичная ссылка',
        max_length=500,
        required=True
    )
