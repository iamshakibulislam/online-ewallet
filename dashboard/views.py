from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from .models import *
from accounts.models import User as u
import checkout_sdk as sdk

@login_required(login_url='/accounts/login/')
def dashboard_index(request):
	user_bal = 0.00
	try :
		curr_bal = UserBalance.objects.get(user=request.user)
		user_bal = curr_bal.balance
		pending_req=money_requests.objects.filter(request_to=request.user).count()
		pending_user_req=money_requests.objects.filter(request_from=request.user).count()
		return render(request,'dashboard/dashboard.html',
			{'balance':user_bal,'pending_req':pending_req,'pending_user_req':pending_user_req})
	except :
		pass
	
	return render(request,'dashboard/dashboard.html',{'balance':user_bal})

@login_required(login_url='/accounts/login/')
def add_fund(request):
	if request.method == 'GET':
		return render(request,'dashboard/add-fund.html')

	if request.method == 'POST':
		amount=int(request.POST['amount'])
		token=request.POST['token']
		if amount == '' or token == '':
			return render(request,'dashboard/add-fund.html',{'BlankError':'All fields are required'})
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
			    		user_bal = UserBalance.objects.get(user=request.user)
			    		curr_bal = user_bal.balance
			    		new_bal=float(curr_bal + amount )
			    		user_bal.balance = new_bal
			    		user_bal.save()
			    		return render(request,'dashboard/add-fund.html',
			    			{'credited':'Fund added successfully !'})
			    	except UserBalance.DoesNotExist:
			    		UserBalance.objects.create(user=request.user,balance=amount)
			    		return render(request,'dashboard/add-fund.html',
			    			{'credited':'Fund added successfully !'})
			    	
			    else:
			    	return render(request,'dashboard/add-fund.html',
			    		{'NoPayment':'your card can not be authorized !'})
			except sdk.errors.CheckoutSdkError as e:
				return render(request,'dashboard/add-fund.html',
					{'PaymentError':'Payment Failed ! Try again later'})

@login_required(login_url='/accounts/login/')
def send_money(request):
	if request.method == 'GET':
		return render(request,'dashboard/send-money.html')

	if request.method == 'POST':
		email = request.POST['email']
		amount = request.POST['amount']

		if email == '' or amount == '' :
			return render(request,'dashboard/send-money.html',
				{'BlankError':'All fields are required'})
		else :

			try :
				recipient = u.objects.get(email=email)
				recipient_bal_data_check = UserBalance.objects.filter(user=recipient).count()
				user_bal_data_check = UserBalance.objects.filter(user=request.user).count()
				if recipient_bal_data_check == 0:
					UserBalance.objects.create(user=recipient,balance=0)
					pass
				if user_bal_data_check == 0 :
					UserBalance.objects.create(user=request.user,balance=0)
					return render(request,'dashboard/send-money.html',
						{'FundError':'Not enough funds !'})

				elif int(amount) > UserBalance.objects.get(user=request.user).balance :
					return render(request,'dashboard/send-money.html',
						{'FundError':'Not enough funds !'})

				else:

					recipient_bal = UserBalance.objects.get(user=recipient)
					recipient_bal.balance = (recipient_bal.balance + int(amount))
					user_bal=UserBalance.objects.get(user=request.user)
					user_bal.balance = (user_bal.balance - int(amount))
					recipient_bal.save()
					user_bal.save()
					return render(request,'dashboard/send-money.html',
						{'success':'Send money successful !'})

			except User.DoesNotExist :
				return render(request,'dashboard/send-money.html',
					{'recipient_not_found':'Recipient does not exist !'})

			

@login_required(login_url='/accounts/login/')
def request_money(request):
	if request.method == 'GET':
		return render(request,'dashboard/request-money.html')

	if request.method == 'POST':
		email=request.POST['email']
		amount=request.POST['amount']

		if email=='' or amount == '':
			return render(request,'dashboard/request-money.html',
				{'BlankError':'All fields are required'})

		else :

			Sender_sel = User.objects.filter(email=email).count()
			if Sender_sel == 0:
				return render(request,'dashboard/request-money.html',
					{'doesnotexist':'Sender does not exist'})

			else:
				sender = User.objects.get(email=email)
				money_requests.objects.create(request_from=request.user,
					request_to=sender,amount=amount
					)
				return render(request,'dashboard/request-money.html',
					{'request_success':'request successful, wait for approval'})


@login_required(login_url='/accounts/login/')
def pending_requests(request):
	sel_requests = money_requests.objects.filter(Q(request_from=request.user) | Q(request_to=request.user))
	return render(request,'dashboard/pending-requests.html',
		{'request_data':sel_requests,'count':sel_requests.count()})

@login_required(login_url='/accounts/login/')
def delete_request(request,id):
	try :
		sel_req=money_requests.objects.get(id=id)
		if sel_req.request_from == request.user or sel_req.request_to == request.user :

			sel_req.delete()
			messages.success(request, "Money request aborted ")
			return redirect('pending_requests')
		else :
			messages.success(request,"Not allowed !")
			return redirect('pending_requests')

	except money_requests.DoesNotExist:
		return redirect('pending_requests')




@login_required(login_url='/accounts/login/')
def approve_request(request,id):
	try :
		sel_req=money_requests.objects.get(id=id)
		if  (sel_req.request_to != request.user):
			messages.success(request,"Permision denied !")
			return redirect('pending_requests')

		if not UserBalance.objects.filter(user=sel_req.request_from).exists():
			UserBalance.objects.create(user=sel_req.request_from,balance=0)
			pass
		if not UserBalance.objects.filter(user=sel_req.request_to).exists():
			UserBalance.objects.create(user=sel_req.request_to,balance=0)
			pass

		user_bal_obj=UserBalance.objects.get(user=request.user)
		rec_bal_obj = UserBalance.objects.get(user=sel_req.request_from)
		if user_bal_obj.balance < sel_req.amount :
			messages.success(request,"Not enough balance ")
			return redirect('pending_requests')
		else :
			user_bal_obj.balance=(user_bal_obj.balance-sel_req.amount)
			user_bal_obj.save()
			rec_bal_obj.balance=(rec_bal_obj.balance + sel_req.amount)
			rec_bal_obj.save()
			sel_req.delete()
			messages.success(request,"Request accepted and paid !")
			return redirect('pending_requests')


	except money_requests.DoesNotExist:
		messages.success(request,"Request not found")
		return redirect('pending_requests')



