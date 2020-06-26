import requests as rq
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from helpers.engine import *
import random
from django.views.decorators.csrf import csrf_exempt
import time
import os


def home(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		return render(request, 'home.html')


get_random_response = lambda intent:random.choice(intent_response_dict[intent])

@csrf_exempt
def chat(requests):
	"""
	Handle Bot Chat
	"""
	if requests.method == 'POST':
		try:
			print(requests.POST)
			post_data = requests.POST
			user_message = post_data['text']

			if user_message == 'Image Provided':
				return JsonResponse({'status':'success','response':'Type start to begin'})

			elif user_message == 'start':
				return JsonResponse({'status':'success','response':'Processing Starting. We will inform you once completed'})
			else:
				response = rq.get('http://localhost:5000/parse',params={'q':user_message})
				response = response.json()
				print(response)
				entities = response.get('entities')
				intent = response.get('intent')['name']
				print('Intent {}, Entities {}'.format(intent,entities))
				if intent == 'gst-info':
					response_text = gst_info(entities)# 'Sorry will get answer soon' #get_event(entities['day'],entities['time'],entities['place'])
				elif intent == 'gst-query':
					response_text = gst_query(entities)
				else:
					response_text = get_random_response(intent)
				return JsonResponse({'status':'success','response':response_text})
		except Exception as e:
			print(e)
			print('issue')
			return JsonResponse({'status':'success','response':'Sorry I am not trained to do that yet...'})



def upload(request):
	return render(request, 'upload_image.html')

@csrf_exempt
def upload_image(request):
	"""
	Handle Image Upload using post request
	"""
	if requests.method == 'POST':
		current_timestamp = time.strftime('%y%m%d-%H%M%S')
		for files in request.FILES:
			#open(settings.BASE_DIR + '/media/' + str(request.FILES[files]), 'wb')
			# file_name = current_timestamp+'_'+str(request.FILES[files])
			file_name = str(request.FILES[files])
			print(file_name)
			file_name_ext = file_name.split('.')[-1]
			if file_name_ext.lower() not in ['jpg','jpeg','png']:
				print('Incorrect FileFormat')
				return 'Incorrect FileFormat'

			file_name_path = os.path.join(settings.MEDIA_ROOT,file_name)
			with open(file_name_path, 'wb') as destination:
				for file_chunk in request.FILES[files].chunks():
					print(file_name_path)
					destination.write(file_chunk) 

