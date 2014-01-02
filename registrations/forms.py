import re

from django import forms

from registrations.models import Registration

class UpdateForm(forms.Form):

    email = forms.EmailField(
        error_messages={'required': 'An email address is required.'}, 
        widget=forms.TextInput(attrs={
            'class':'form-control gray',
            'placeholder': 'Email Address',
        })
    )

    def clean_email(self):
        email_data = self.cleaned_data['email']    
        try:
            r = Registration.objects.get(email=email_data)
            return email_data
        except Registration.DoesNotExist:
            raise forms.ValidationError("Could not find that email address.")

class UpdateDataForm(forms.Form):

    zip_code = forms.CharField(
        error_messages={'required': 'Your zip code is required.'}, 
        widget=forms.TextInput(attrs={
            'class':'form-control gray',
            'placeholder': 'Zip Code',
        })
    )
    
    def clean_zip_code(self):        
        zip_data = self.cleaned_data['zip_code']
        
        if re.search(r'^\d{5}(?:-\d{4})?$', zip_data):
            return zip_data
        else:
            raise forms.ValidationError('Enter a zip code in the format XXXXX or XXXXX-XXXX.')

class RegistrationForm(forms.Form):

    email = forms.EmailField(
        error_messages={'required': 'An email address is required.'}, 
        widget=forms.TextInput(attrs={
            'class':'form-control blue',
            'placeholder': 'Your Email Address',
            'maxlength': '50',
        })
    )
    
    zip_code = forms.CharField(
        error_messages={'required': 'Your zip code is required.'}, 
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder': 'Zip Code',
            'maxlength': '5',
        })
    )
    
    def clean_zip_code(self):        
        zip_data = self.cleaned_data['zip_code']
        
        if re.search(r'^\d{5}(?:-\d{4})?$', zip_data):
            return zip_data
        else:
            raise forms.ValidationError('Enter a zip code in the format XXXXX or XXXXX-XXXX.')
    
    def clean_email(self):
        email_data = self.cleaned_data['email']
        
        try:
            r = Registration.objects.get(email=email_data)
            # If the email exists but the status is 0 (unconfirmed), let it pass
            if r.status == 0:
                return email_data
            else:
                raise forms.ValidationError("That email address is already registered.")
        except Registration.DoesNotExist:
            return email_data
        
