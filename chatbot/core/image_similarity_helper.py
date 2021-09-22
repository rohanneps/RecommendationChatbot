"""
Module contains Class for computing image similarity
"""


import os
import numpy as np
import pandas as pd
from django.conf import settings

from tensorflow.keras.applications import VGG16, imagenet_utils
from tensorflow.keras.preprocessing.image import load_img, img_to_array


class ImageSimilarity:
    """
    Class for computing image similarity between query image
    and catalog SERP images
    """

    def __init__(
        self, catalog_df: pd.DataFrame, image_dir: str, search_image_path: str
    ) -> None:
        self.catalog_df = catalog_df
        self.image_dir = image_dir
        self.search_image_path = search_image_path
        # Feature Extractor Model Details
        print("Loading Model")
        self.model = VGG16(weights="imagenet", include_top=False)
        self.input_shape = (224, 224)
        self.preprocess = imagenet_utils.preprocess_input

    def generate_image_similarity_index(self) -> None:
        """
        Compute image similarity between query image
        and catalog SERP images

        Args:
        -----
                None

        Returns:
        --------
                None
        """
        image_name_list = range(1, len(self.catalog_df) + 1)
        image_location_list = list(
            map(
                lambda image_file_prefix: os.path.join(
                    self.image_dir,
                    settings.IMAGE_FILE_NAME_FORMAT.format(image_file_prefix),
                ),
                image_name_list,
            )
        )

        # Appending Source images to the front of the list for bulk prediction
        image_location_list = [self.search_image_path] + image_location_list

        # print(image_location_list)
        image_array_list = []

        # Preprocessing for Batch Prediction
        for img_path in image_location_list:
            try:
                image = load_img(img_path)
                image = image.resize(self.input_shape)
                image = img_to_array(image)
                image = self.preprocess(image)
                image_array_list.append(image)
            except:
                print(f"Exception in image: {img_path}")

        images_np_array = np.array(image_array_list)

        # Batch Prediction
        print("Batch Prediction")
        images_features_predicted = self.model.predict(images_np_array)

        source_image_embeddings = images_features_predicted[0]

        # Compute euclidean distance between source and serp images
        euclidean_distance_list = []

        for serp_image_embeddings in images_features_predicted[1:]:
            # Computing the euclidean distance between the image tensors
            euclidean_distance_list.append(
                np.linalg.norm(source_image_embeddings - serp_image_embeddings)
            )

        self.catalog_df["source_image_distance"] = euclidean_distance_list
        self.catalog_df["image_similarity_weightage"] = (
            self.catalog_df["source_image_distance"].rank(ascending=True).astype(int)
        )
        self.catalog_df["image_similarity_weightage"] = (
            settings.IMAGE_WEIGHTAGE / self.catalog_df["image_similarity_weightage"]
        )
