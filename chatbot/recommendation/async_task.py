from __future__ import absolute_import

from celery import shared_task,task
from core.ProcessHandler import ProcessHandler
from recommendation.models import Process
from chatbot.celery_settings import app as celery_app
import traceback
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

comp_logger = logging.getLogger(__name__)



# to start the celery worker daemon
# celery worker -A chatbot.celery_settings -l info
# flower -A chatbot --port=5555   --> to view error log of celery


@shared_task(bind=True)
def start_background_recommendation(self, user_recom_process_id):
	comp_logger.info('Initiating Recommendation Sequece for id:{}'.format(user_recom_process_id))
	user_recom_process_obj = Process.objects.get(id=user_recom_process_id)


	# project_status = ProjectStatus.objects.get(project=project)
	# async_task_id = self.request.id
	# project_status.asynctask_id = async_task_id
	# project_status.save()

	process_handler = ProcessHandler(user_recom_process_obj)
	try:
		process_handler.main()

		# send task completed message
		channel_layer = get_channel_layer()
		bot_message = 'Task completed. Please link on this <a href=\'www.google.com\'>link</a> to view.'
		channel_user_id = user_recom_process_obj.user.id
		# Trigger bot message to user
		async_to_sync(channel_layer.group_send)(
			str(channel_user_id),  # Channel Name, Should always be string
			{
				"type": "notify",   # Custom Function written in the consumers.py
				"text": bot_message,
			},
		)
	except Exception as e:
		# Console exception display and bot_messagebase persistance
		traceback_error = traceback.format_exc()
		comp_logger.info(traceback_error)
		process_handler.update_project_status('Failed', str(e))

