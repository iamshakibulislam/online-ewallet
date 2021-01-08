from django import forms

class UserForm(forms.Form):

	full_name=forms.CharField(max_length=20,required=True,
		widget=forms.TextInput(attrs={'class':'form-control','placeholder':'full name'}))
	email=forms.EmailField(max_length=50,required=True,
		widget=forms.TextInput(attrs={'class':'form-control','placeholder':'email'}))
	address=forms.CharField(max_length=60,required=True,
		widget=forms.TextInput(attrs={'class':'form-control','placeholder':'address'}))
	password1=forms.CharField(max_length=20,required=True,
		widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
	password2=forms.CharField(max_length=20,required=True,
		widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm password'}))

