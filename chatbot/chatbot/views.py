import requests as rq
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from helpers.engine import *
import random
from django.views.decorators.csrf import csrf_exempt
import time
import os
import logging


comp_logger = logging.getLogger(__name__)

def home(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		return render(request, 'home.html')


get_random_response = lambda intent:random.choice(intent_response_dict[intent])

# @csrf_exempt
# def bot_response(requests):
# 	"""
# 	Handle Bot Chat Response
# 	"""
# 	if requests.method == 'POST':
# 		try:
# 			print(requests.POST)
# 			post_data = requests.POST
# 			user_message = post_data['text']

# 			if user_message == 'Image Provided':
# 				return JsonResponse({'status':'success','response':'Type start to begin'})

# 			elif user_message == 'start':
# 				return JsonResponse({'status':'success','response':'Processing Starting. We will inform you once completed'})
			
# 			elif user_message == 'Image not provided':
# 				return JsonResponse({'status':'success','response':'Please provide an image to continue. Applicable exntesions are png, jpg, jpeg'})
			
# 			elif user_message in ['hi','hey','hello','howdy']:
# 				response_text = 'hi'
# 				response_text = response_text + '\n' + 'What would you like me to recommed you today?'
# 				request.session['user_stage'] = 1
# 				return JsonResponse({'status':'success','response':response_text})

# 			else:
# 				response = rq.get('http://localhost:5000/parse',params={'q':user_message})
# 				response = response.json()
# 				print(response)
# 				entities = response.get('entities')
# 				intent = response.get('intent')['name']
# 				print('Intent {}, Entities {}'.format(intent,entities))
# 				if intent == 'gst-info':
# 					response_text = gst_info(entities)# 'Sorry will get answer soon' #get_event(entities['day'],entities['time'],entities['place'])
# 				elif intent == 'gst-query':
# 					response_text = gst_query(entities)
# 				else:
# 					response_text = get_random_response(intent)
# 				return JsonResponse({'status':'success','response':response_text})
# 		except Exception as e:
# 			print(e)
# 			print('issue')
# 			return JsonResponse({'status':'success','response':'Sorry I am not trained to do that yet...'})


def intialize_session_variables(requests):
	if 'user_stage' not in requests.session:
		requests.session['user_stage'] = 0

	if 'user_process_running' not in requests.session:
		requests.session['user_process_running'] = False

	if 'user_search_term' not in requests.session:
		requests.session['user_search_term'] = None
	return requests

@csrf_exempt
def bot_response(requests):
	"""
	Handle Bot Chat Response
	"""

	if requests.method == 'POST':
		comp_logger.info(requests.POST)
		post_data = requests.POST
		user_message = post_data['text'].lower()
		comp_logger.info('user: {}'.format(user_message))
		
		response_text = None
		requests = intialize_session_variables(requests)

		if user_message in ['clear','no','stop','restart','pause','halt','terminate','end', 'close', 'exit']:
			if 'user_stage' in requests.session:
				requests.session['user_stage'] = 0
				requests.session['user_process_running'] = False
			if 'user_search_term' in requests.session:
				requests.session['user_search_term'] = None

			response_text = 'Search Operation {}.'.format(user_message)

		comp_logger.info('user: user_stage: {}'.format(requests.session['user_stage']))
		comp_logger.info('user: user_process_running: {}'.format(requests.session['user_process_running']))

		if not response_text:
			user_stage = requests.session['user_stage']
			user_process_running = requests.session['user_process_running']

			# if user_message == 'image provided':
			# 	response_text = 'Type start to begin'

			if user_message == 'image not provided':
				response_text = 'Please provide an image to continue. Applicable exntesions are png, jpg, jpeg'

			elif user_message in ['hi','hey','hello','howdy']:
				response_text = 'hi'
				if not user_process_running :
					response_text = response_text + '\n' + 'What would you like me to recommed you today?'
					requests.session['user_stage'] = 1
			
			elif user_message == 'start':
				if requests.session['user_stage'] !=3:
					response_text = 'Please provide search query and image first'
				elif user_process_running :
					response_text = 'Processing already underway.'
				else:
					response_text = 'Processing Starting. We will inform you once completed'
					requests.session['user_process_running'] = True

			elif not user_process_running :
				if user_message == 'image provided':
					response_text = 'Type start to begin'
					requests.session['user_stage'] = 3
			
				elif user_message == 'image not provided':
					response_text = 'Please provide an image to continue. Applicable exntesions are png, jpg, jpeg'
				
				else:
					response_text = 'You have provided the search term: {}, now please provide an image'.format(user_message)
					requests.session['user_stage'] = 2
					requests.session['user_search_term'] = user_message

			else:
				# task in progress
				response_text = 'Please wait for the current task to finish'

		comp_logger.info('bot: {}'.format(response_text))
		return JsonResponse({'status':'success','response':response_text})


@csrf_exempt
def upload_image(request):
	"""
	Handle Image Upload using post request
	"""
	if request.FILES:
		current_timestamp = time.strftime('%y%m%d-%H%M%S')
		for files in request.FILES:
			#open(settings.BASE_DIR + '/media/' + str(request.FILES[files]), 'wb')
			# file_name = current_timestamp+'_'+str(request.FILES[files])
			file_name = str(request.FILES[files])
			if file_name:
				# there is image upload
				file_name_ext = file_name.split('.')[-1]
				print(file_name_ext)
				if file_name_ext.lower() not in ['jpg','jpeg','png']:
					print('Incorrect FileFormat')
					return 'Incorrect FileFormat'

				file_name_path = os.path.join(settings.MEDIA_ROOT,file_name)
				with open(file_name_path, 'wb') as destination:
					for file_chunk in request.FILES[files].chunks():
						print(file_name_path)
						destination.write(file_chunk) 
				return 'Success'
	else:
		return HttpResponseRedirect(reverse('home'))