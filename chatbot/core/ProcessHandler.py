from django.conf import settings
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import urllib.parse
import os

from helpers import helper
from .generate_html import get_html_from_dataframe
from .ImageSimilarity import ImageSimilarity
from .serp_helper import (
							getAmazonSerpCatalog,
							getGoogleSerpCatalog,
							getEbaySerpCatalog,
							getWalmartSerpCatalog,
						)
from .text_similarity_helper import generateSimilarity

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

import logging
comp_logger = logging.getLogger(__name__)


class ProcessHandler(object):

	def __init__(self, project):

		comp_logger.info('Initializing Process')
		# initialize firefox driver
		options = Options()
		options.headless = True
		self.driver = webdriver.Firefox(options=options, executable_path=settings.GECKO_DRIVER_PATH)
		
		# Process instance settings		
		self.project = project
		self.project_id = self.project.id
		self.query = self.project.search_query
		self.user = self.project.user
		self.search_image = os.path.join(settings.BASE_DIR, self.project.search_image)
		self.project_dir = os.path.join(settings.PROCESS_FOLDER, str(self.project_id))

		self.recommendation_html_file_path = os.path.join(self.project_dir, settings.RECOMMEDATION_HTML_FILE)
		self.recommendation_html_screenshot = os.path.join(self.project_dir, settings.RECOMMENDATION_SCREENSHOT)
		self.image_dir = os.path.join(self.project_dir, settings.IMAGES_FOLDER)
		self.page_source_dir = os.path.join(self.project_dir, settings.PAGE_SOURCE_FOLDER)

		# Process image file path to be used
		self.search_image_path = os.path.join(self.project_dir, settings.SOURCE_IMAGE_PATH)
		
		helper.create_dir(self.project_dir)
		helper.create_dir(self.image_dir)
		helper.create_dir(self.page_source_dir)

		helper.copy_file(self.search_image, self.search_image_path)

		self.catalog_df = pd.DataFrame(columns=settings.SERP_PRODUCT_CATALOG_HEADERS)


	def driver_get_page_source(self, url, file_name):
		self.driver.get(url)
		platform_page_data = self.driver.page_source
		helper.download_page_source(platform_page_data, file_name)

		# with open(file_name, 'r') as f:
		# 	platform_page_data = f.read()
		return platform_page_data


	def get_marketplace_catalog_df(self):
		# Generating url encoded query strings
		url_encode_query = urllib.parse.quote(self.query)
		amazon_q_string = settings.AMAZON_SERP_QUERY_STRING.format(url_encode_query)
		google_q_string = settings.GOOGLE_SERP_QUERY_STRING.format(url_encode_query)
		ebay_q_string = settings.EBAY_SERP_QUERY_STRING.format(url_encode_query)
		walmart_q_string = settings.WALMART_SERP_QUERY_STRING.format(url_encode_query)

		
		comp_logger.info('Getting Amazon Details')
		amazon_file_path = os.path.join(self.page_source_dir, settings.AMAZON_PAGE_SOURCE)
		amazon_page_source = self.driver_get_page_source(amazon_q_string, amazon_file_path)
		amazon_catalog_df = getAmazonSerpCatalog(amazon_page_source, settings.SERP_PRODUCT_CATALOG_HEADERS)
		self.catalog_df = self.catalog_df.append(amazon_catalog_df)

		comp_logger.info('Getting Google Details')
		google_file_path = os.path.join(self.page_source_dir, settings.GOOGLE_PAGE_SOURCE)
		google_page_source = self.driver_get_page_source(google_q_string, google_file_path)
		google_catalog_df = getGoogleSerpCatalog(google_page_source, settings.SERP_PRODUCT_CATALOG_HEADERS)
		self.catalog_df = self.catalog_df.append(google_catalog_df)

			
		comp_logger.info('Getting Ebay Details')
		ebay_file_path = os.path.join(self.page_source_dir, settings.EBAY_PAGE_SOURCE)
		ebay_page_source = self.driver_get_page_source(ebay_q_string, ebay_file_path)
		try:
			ebay_catalog_df = getEbaySerpCatalog(ebay_page_source, settings.SERP_PRODUCT_CATALOG_HEADERS)
			self.catalog_df = self.catalog_df.append(ebay_catalog_df)
		except:
			pass
		# to do for walmart

		comp_logger.info('Writing Merged File')

	def save_merged_platformat_file(self):
		self.catalog_df.to_csv(os.path.join(self.project_dir, settings.RECOMMENDATION_MERGED), index=False,sep='\t')


	def clean_resource():
		self.driver.close()


	def download_result_images(self):
		self.catalog_df['image_file_name'] = range(1,len(self.catalog_df)+1)
		
		def process_image_row(row):
			image_path = os.path.join(self.image_dir, settings.IMAGE_FILE_NAME_FORMAT.format(row['image_file_name']))
			helper.download_image(row['Image'], image_path)
		
		self.catalog_df.apply(process_image_row, axis = 1)
		

	def image_similarity_process(self):
		comp_logger.info('Downloading Images')
		self.download_result_images()

		comp_logger.info('Computing product image similiarity index')
		image_similarity_helper_obj = ImageSimilarity(self.catalog_df, self.image_dir, self.search_image_path)
		image_similarity_helper_obj.generate_image_similarity_index()
		self.catalog_df = image_similarity_helper_obj.catalog_df



	def text_similarity_process(self):
		comp_logger.info('Computing product name similarity')
		self.catalog_df = generateSimilarity(self.catalog_df, self.query, 'Name')
		self.catalog_df = self.catalog_df.sort_values(by=['TFIDF_COSINE','Price','Name'],ascending=True)


	def generate_html_response(self):
		comp_logger.info('Generating System Response')
		get_html_from_dataframe(self.catalog_df, self.query, self.recommendation_html_file_path)
		self.get_html_screenshot()

	def get_html_screenshot(self):
		self.driver.get('file://'+ os.path.join(settings.BASE_DIR, self.recommendation_html_file_path))
		self.driver.save_screenshot(self.recommendation_html_screenshot)


	def generate_top_n_picks(self):
		top_n_pricks_list = []
		cnt = 1
		def top_n_picks(row):
			nonlocal cnt
			name = row['Name']
			url = row['Url']
			top_n_pricks_list.append('{}.\t{}\t\t{}\n\n'.format(cnt, name, url))
			cnt += 1
			
		self.catalog_df[['Name','Url']].iloc[:settings.TOP_N_PICKS].apply(top_n_picks, axis=1)
		self.top_n_picks_recommendation = '\n'.join(top_n_pricks_list)


	def update_project_status(self, status, failed_log=None):
		if failed_log:
			self.project.failed_log = failed_log
		self.project.status = status
		self.project.save()


	def main(self):
		comp_logger.info('For query {} and user {}'.format(self.query, self.user))
		self.get_marketplace_catalog_df()
		
		if len(self.catalog_df)> 0 :
			self.image_similarity_process()
			self.text_similarity_process()
			self.catalog_df['serp_weightage'] = self.catalog_df['image_similarity_weightage'] + self.catalog_df['text_match_weightage']
			self.catalog_df.sort_values(by=['serp_weightage'], ascending=False, inplace=True)

			# self.generate_html_response()
			# self.generate_top_n_picks()
			self.save_merged_platformat_file()
			comp_logger.info('Process completed for: {}'.format(self.project_id))
		else:
			comp_logger.info('No Results')


		# Task completed
		self.update_project_status('Completed')