from django.db import models
from accounts.models import User
import datetime
class UserBalance(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	balance=models.FloatField(blank=False,null=False)

	def __str__(self):
		return self.user.email



class money_requests(models.Model) :
	date = models.DateField(blank=False,null=False,default=datetime.date.today)
	request_from = models.ForeignKey(User,on_delete=models.CASCADE,related_name='request_from')
	request_to = models.ForeignKey(User,on_delete=models.CASCADE,related_name='request_to')
	amount = models.FloatField(blank=False,null=False,default=0)
	is_pending = models.BooleanField(blank=False,default=True)

	def __str__(self):
		return str(self.request_from.full_name +' to '+self.request_to.full_name)

	class Meta:
		verbose_name_plural = 'money requests'
