from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

# Create your models here.

class Process(models.Model):
	class Meta:
		verbose_name_plural = 'Recommendation Processes'

	status_list = (
		('Pending', 'Pending'),
		('InProgress', 'InProgress'),
		('Completed', 'Completed'),
		('Failed', 'Failed'),
		('Terminated','Terminated'),
	)

	user = models.ForeignKey(User, on_delete = models.CASCADE)
	start_date = models.DateTimeField(auto_now=False, auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
	search_query = models.CharField(max_length=140, blank=False, null=False)
	search_image = models.CharField(max_length=140, blank=False, null=False)
	status = models.CharField(max_length=20,choices=status_list,blank=False, null=False)
	failed_log = models.CharField(max_length=1500, blank=True,null=True)
	output_file = models.CharField(max_length=140, blank=False, null=False, default='')
	
	def __str__(self):
		return str(self.id)



def get_initiated_user_process(user):
	"""
	Return Unintiated User Process
	"""
	user_lookup = (Q(user=user))
	return Process.objects.filter(status='Pending').filter(user_lookup).distinct().order_by('-id')


def get_inprogress_user_process(user):
	"""
	Return Running User Process
	"""
	user_lookup = (Q(user=user))
	return Process.objects.filter(status='InProgress').filter(user_lookup).distinct().order_by('-id')