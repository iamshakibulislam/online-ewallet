from django.shortcuts import render,redirect
from accounts.forms import UserForm
from django.http import HttpResponse
import json
import requests
from accounts.models import User
from django.contrib import auth



def registration_page(request):
	if request.method=='GET':
		UserCreationForm=UserForm
		return render(request,'registration.html',{'form':UserCreationForm})

	if request.method=='POST':
		UserCreationForm=UserForm(request.POST)
		if UserCreationForm.is_valid():
			context={}
			full_name=UserCreationForm.cleaned_data['full_name']
			email=UserCreationForm.cleaned_data['email']
			address=UserCreationForm.cleaned_data['address']
			password1=UserCreationForm.cleaned_data['password1']
			password2=UserCreationForm.cleaned_data['password2']
			Captcha_response=request.POST['g-recaptcha-response']
			secret_key='6Lco6RwaAAAAAPplcNfJsiKRBXvHXQzFRyPzXesO'
			sending_request=requests.post('https://www.google.com/recaptcha/api/siteverify',
				data={'response':Captcha_response,'secret':secret_key})
			status=json.loads(sending_request.text)['success']

			if password1 != password2 :
				context['passerror']='password did not match'
				context['form']=UserForm
				return render(request,'registration.html',context)

			elif status == False :
				context['form']=UserForm
				context['captcha_error']='captcha validation failed'
				return render(request,'registration.html',context)

			else:
				try:
					User.objects.get(email=email)

					return render(request,'registration.html',
						{'form':UserForm,'userexist':'user aready exists'})
				except User.DoesNotExist:
					create_user=User.objects.create_user(password=password1,full_name=full_name,email=email,
						address=address)
					return render(request,'registration.html',
						{'form':UserForm,'success':'account created successfully.You can login now'})







def login_page(request):

	if request.method == 'GET':
		return render(request,'login.html')

	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']

		authenticate=auth.authenticate(request,email=email,password=password)
		print(authenticate)
		if authenticate is not None :
			auth.login(request,authenticate)

			return redirect('dashboard_index')

		else:
			return render(request,'login.html',{'message':'username or password is incorrect !'})


def user_logout(request):
	auth.logout(request)
	return redirect('index_page')
