from django.shortcuts import render,get_object_or_404
from accounts.forms import UserForm
from django.http import HttpResponse
import json
import requests
from accounts.models import User
from dashboard.models import *
from django.contrib import auth
import checkout_sdk as sdk


def index_page(request):
	return render(request,'index.html')


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
			return HttpResponse('<h1>user is authenticated</>')

		else:
			return render(request,'login.html',{'message':'username or password is incorrect !'})


def donate(request):
	if request.method == 'GET':
		rec_id=request.GET['user']
		user=get_object_or_404(User,id=rec_id)
		return render(request,'donate-page.html',{'id':user.id,'name':user.full_name})

	if request.method == 'POST':
		amount=int(request.POST['amount'])
		token=request.POST['token']
		userid = request.POST['id']
		if amount == '' or token == '':
			return render(request,'donate-page.html',{'BlankError':'All fields are required'})
		else:
			api = sdk.get_api(secret_key='sk_test_f2a38861-4256-413b-a95c-4c3822b8f508')

			try:
			    payment = api.payments.request(
			        source={
			            'token': token,
			        },
			        amount=amount*100,
			        currency=sdk.Currency.USD,
			        
			    )


			    if payment.approved == True and payment.status ==  "Authorized":
			    	try :

			    		user_bal = UserBalance.objects.get(user__id=int(userid))
			    		curr_bal = user_bal.balance
			    		new_bal=float(curr_bal + int(amount) )
			    		user_bal.balance = new_bal
			    		user_bal.save()
			    		return render(request,'donate-page.html',
			    			{'credited':'Donation successful !'})
			    	except UserBalance.DoesNotExist:
			    		UserBalance.objects.create(user_id=userid,balance=int(amount))
			    		return render(request,'donate-page.html',
			    			{'credited':'Donation successful !'})
			    	
			    else:
			    	return render(request,'donate-page.html',
			    		{'NoPayment':'your card can not be authorized !'})
			except sdk.errors.CheckoutSdkError as e:
				
				return render(request,'donate-page.html',
					{'PaymentError':'Payment Failed ! Try again later'})