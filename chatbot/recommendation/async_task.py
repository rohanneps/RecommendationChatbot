from __future__ import absolute_import

from celery import shared_task,task
from core.ProcessHandler import ProcessHandler
from recommendation.models import Process
from chatbot.celery_settings import app as celery_app
import traceback
import logging

comp_logger = logging.getLogger(__name__)



# to start the celery worker daemon
# celery worker -A chatbot.celery_settings -l info
# flower -A chatbot --port=5555   --> to view error log of celery


@shared_task(bind=True)
def start_async_background_recommendation(self, user_recom_process_id):
	comp_logger.info('Initiating Recommendation Sequece for id:{}'.format(user_recom_process_id))
	user_recom_process_obj = Process.objects.get(id=user_recom_process_id)


	# project_status = ProjectStatus.objects.get(project=project)
	# async_task_id = self.request.id
	# project_status.asynctask_id = async_task_id
	# project_status.save()

	process_handler = ProcessHandler(user_recom_process_obj)
	try:
		process_handler.main()
	except Exception as e:
		# Console exception display and database persistance
		traceback_error = traceback.format_exc()
		comp_logger.info(traceback_error)
		process_handler.update_project_status('Failed', str(e))