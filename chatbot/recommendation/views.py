from django.shortcuts import reverse, render
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect
from .models import Process
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import pandas as pd
import logging
import os
comp_logger = logging.getLogger(__name__)

# Create your views here.

class RecommendationListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGOUT_REDIRECT_URL
	redirect_field_name = 'redirect_to'
	queryset = Process.objects.all().order_by('-id')
	template_name = 'process/list.html'
	context_object_name = 'process_list'
	paginate_by = 10

	def get_queryset(self):
		query = self.request.GET.get("q")
		query_user = self.request.user
		process_objects = Process.objects.filter(user=query_user)
		if query and query not in ['',' ']:
			comp_logger.info('Process search for term: {}.'.format(query))
			prospect_lookup = (Q(search_query__icontains=query) | Q(status__icontains=query) |
							   Q(search_image__icontains=query))
			return process_objects.filter(prospect_lookup).distinct().order_by('-id')
		else:
			return process_objects.order_by('-id')


class RecommendationDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGOUT_REDIRECT_URL
	redirect_field_name = 'redirect_to'
	context_object_name = 'recommendation_obj'
	template_name = 'process/detail.html'
	queryset = Process.objects.all()

	def get(self, request, *args, **kwargs):
		# authenticating if user has access to this recommendation
		self.object = self.get_object()
		if self.request.user != self.object.user:
			return HttpResponseRedirect(reverse('home'))
		else:
			return super(RecommendationDetailView, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(RecommendationDetailView, self).get_context_data(**kwargs)
		recommendation_details = self.get_recommendation_details()
		context['recommendation_details'] = recommendation_details
		return context


	def get_recommendation_details(self):
		current_object_id = self.object.id
		process_objects = Process.objects.filter(id=current_object_id)
		project_dir = os.path.join(settings.PROCESS_FOLDER, str(current_object_id))
		df = pd.read_csv(os.path.join(project_dir, settings.RECOMMENDATION_MERGED), sep='\t')
		# taking top 10 records
		df = df.iloc[:settings.TOP_N_PICKS]
		df['id'] = list(range(1,len(df)+1))
		return df.to_dict('records')