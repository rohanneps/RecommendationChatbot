from keras.applications import VGG16
from keras.applications import imagenet_utils
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
import numpy as np
from django.conf import settings
import os

class ImageSimilarity(object):

	def __init__(self, catalog_df, image_dir, search_image_path):
		self.catalog_df = catalog_df
		self.image_dir = image_dir
		self.search_image_path = search_image_path
		# Feature Extractor Model Details
		print('Loading Model')
		self.model = VGG16(weights='imagenet', include_top=False)
		self.inputShape = (224, 224)
		self.preprocess = imagenet_utils.preprocess_input


	def generate_image_similarity_index(self):
		image_name_list = range(1,len(self.catalog_df)+1)
		image_location_list = list(map(lambda image_file_prefix: os.path.join(self.image_dir, settings.IMAGE_FILE_NAME_FORMAT.format(image_file_prefix)), image_name_list))

		# Appending Source images to the front of the list for bulk prediction
		image_location_list = [self.search_image_path] + image_location_list

		# print(image_location_list)
		image_array_list = []

		for img_path in image_location_list:
			try:
				image = load_img(img_path)
				image = image.resize(self.inputShape)
				image = img_to_array(image)
				image = self.preprocess(image)
				image_array_list.append(image)
			except:
				print('Exception in image: {}'.format(img_path))


		images_np_array = np.array(image_array_list)
		# Batch Prediction
		print('Batch Prediction')
		images_features_predicted = self.model.predict(images_np_array)

		source_image_embeddings = images_features_predicted[0]

		euclidean_distance_list = []

		for result_image_index in range(1,len(images_features_predicted)):
			# Computing the euclidean distance between the image tensors
			euclidean_distance_list.append(np.linalg.norm(source_image_embeddings-images_features_predicted[result_image_index]))

		self.catalog_df['source_image_distance'] = euclidean_distance_list
		self.catalog_df['image_similarity_weightage'] = self.catalog_df['source_image_distance'].rank(ascending=True).astype(int)
		self.catalog_df['image_similarity_weightage'] = settings.IMAGE_WEIGHTAGE/self.catalog_df['image_similarity_weightage']