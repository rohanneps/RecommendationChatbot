from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

# Create your models here.

class Process(models.Model):
	class Meta:
		verbose_name_plural = 'Recommendation Processes'

	user = models.ForeignKey(User, on_delete = models.CASCADE)
	start_date = models.DateTimeField(auto_now=False, auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
	search_query = models.CharField(max_length=140, blank=False, null=False)
	search_image = models.CharField(max_length=140, blank=False, null=False)
	initiated = models.BooleanField(default=False)
	completed = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)



def get_initiated_user_process(user):
	"""
	Return Unintiated User Process
	"""
	user_lookup = (Q(user=user))
	return Process.objects.filter(initiated=False).filter(user_lookup).distinct().order_by('-id')
