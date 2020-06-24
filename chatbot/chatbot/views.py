import requests as rq
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from helpers.engine import *
import random
from django.views.decorators.csrf import csrf_exempt

def home(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		return render(request, 'home.html')


get_random_response = lambda intent:random.choice(intent_response_dict[intent])

@csrf_exempt
def chat(requests):
	if requests.method == 'POST':
		try:
			print(requests.POST)
			post_data = requests.POST
			user_message = post_data["text"]
			response = rq.get("http://localhost:5000/parse",params={"q":user_message})
			response = response.json()
			print(response)
			entities = response.get("entities")
			intent = response.get("intent")['name']
			print("Intent {}, Entities {}".format(intent,entities))
			if intent == "gst-info":
				response_text = gst_info(entities)# "Sorry will get answer soon" #get_event(entities["day"],entities["time"],entities["place"])
			elif intent == "gst-query":
				response_text = gst_query(entities)
			else:
				response_text = get_random_response(intent)
			return JsonResponse({"status":"success","response":response_text})
		except Exception as e:
			print(e)
			print('issue')
			return JsonResponse({"status":"success","response":"Sorry I am not trained to do that yet..."})
