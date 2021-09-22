"""
Contains Process Handler Class

"""
import os
import logging
import warnings
import urllib.parse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from django.conf import settings

from helpers import helper
from .generate_html import get_html_from_dataframe
from .image_similarity_helper import ImageSimilarity
from .text_similarity_helper import compute_query_catalog_similarity

from .serp_helper import (
    get_amazon_serp_catalog,
    get_google_serp_catalog,
    get_ebay_serp_catalog,
)


warnings.filterwarnings("ignore")


comp_logger = logging.getLogger(__name__)


class ProcessHandler:
    """
    Class that handles the process stages
    """

    def __init__(self, project) -> None:

        comp_logger.info("Initializing Process")
        # initialize firefox driver
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options, executable_path=settings.GECKO_DRIVER_PATH
        )

        # Process instance settings
        self.project = project
        self.project_id = self.project.id
        self.query = self.project.search_query
        self.user = self.project.user
        self.search_image = os.path.join(settings.BASE_DIR, self.project.search_image)
        self.project_dir = os.path.join(settings.PROCESS_FOLDER, str(self.project_id))

        self.recommendation_html_file_path = os.path.join(
            self.project_dir, settings.RECOMMEDATION_HTML_FILE
        )
        self.recommendation_html_screenshot = os.path.join(
            self.project_dir, settings.RECOMMENDATION_SCREENSHOT
        )
        self.image_dir = os.path.join(self.project_dir, settings.IMAGES_FOLDER)
        self.page_source_dir = os.path.join(
            self.project_dir, settings.PAGE_SOURCE_FOLDER
        )

        # Process image file path to be used
        self.search_image_path = os.path.join(
            self.project_dir, settings.SOURCE_IMAGE_PATH
        )

        helper.create_dir(self.project_dir)
        helper.create_dir(self.image_dir)
        helper.create_dir(self.page_source_dir)

        helper.copy_file(self.search_image, self.search_image_path)

        self.top_n_picks_recommendation = ""
        self.catalog_df = pd.DataFrame(columns=settings.SERP_PRODUCT_CATALOG_HEADERS)

    def driver_get_page_source(self, url: str, file_name: str) -> str:
        """
        Return Page Source for a given url and save it to a flat file

        Args:
        -----
                url (str): URL for page source
                file_name (str): file path to download the page source

        Returns:
        --------
                Page source of the url
        """
        self.driver.get(url)
        platform_page_data = self.driver.page_source
        helper.download_page_source(platform_page_data, file_name)

        # with open(file_name, 'r') as f:
        # 	platform_page_data = f.read()
        return platform_page_data

    def get_marketplace_catalog_df(self) -> None:
        """
        Create a dataframe containing the SERP results from AMAZON,
        GOOGLE and EBAY

        Args:
        -----
                None
        Returns:
        --------
                None
        """
        # Generating url encoded query strings
        url_encode_query = urllib.parse.quote(self.query)

        # GENERATE QUERY STRINGS FOR EACH PLATFORM
        amazon_q_string = settings.AMAZON_SERP_QUERY_STRING.format(url_encode_query)
        google_q_string = settings.GOOGLE_SERP_QUERY_STRING.format(url_encode_query)
        ebay_q_string = settings.EBAY_SERP_QUERY_STRING.format(url_encode_query)
        # walmart_q_string = settings.WALMART_SERP_QUERY_STRING.format(url_encode_query)

        comp_logger.info("Getting Amazon Details")
        amazon_file_path = os.path.join(
            self.page_source_dir, settings.AMAZON_PAGE_SOURCE
        )
        amazon_page_source = self.driver_get_page_source(
            amazon_q_string, amazon_file_path
        )
        amazon_catalog_df = get_amazon_serp_catalog(
            amazon_page_source, settings.SERP_PRODUCT_CATALOG_HEADERS
        )
        self.catalog_df = self.catalog_df.append(amazon_catalog_df)

        comp_logger.info("Getting Google Details")
        google_file_path = os.path.join(
            self.page_source_dir, settings.GOOGLE_PAGE_SOURCE
        )
        google_page_source = self.driver_get_page_source(
            google_q_string, google_file_path
        )
        google_catalog_df = get_google_serp_catalog(
            google_page_source, settings.SERP_PRODUCT_CATALOG_HEADERS
        )
        self.catalog_df = self.catalog_df.append(google_catalog_df)

        comp_logger.info("Getting Ebay Details")
        ebay_file_path = os.path.join(self.page_source_dir, settings.EBAY_PAGE_SOURCE)
        ebay_page_source = self.driver_get_page_source(ebay_q_string, ebay_file_path)
        try:
            ebay_catalog_df = get_ebay_serp_catalog(
                ebay_page_source, settings.SERP_PRODUCT_CATALOG_HEADERS
            )
            self.catalog_df = self.catalog_df.append(ebay_catalog_df)
        except:
            pass
        # to do for walmart

        comp_logger.info("Writing Merged File")

    def save_merged_platformat_file(self) -> None:
        """
        Save the catalog dataframe
        Args:
        -----
                None
        Returns:
        --------
                None
        """
        self.catalog_df.to_csv(
            os.path.join(self.project_dir, settings.RECOMMENDATION_MERGED),
            index=False,
            sep="\t",
        )

    def clean_resource(self) -> None:
        """
        Close resources opened
        Args:
        -----
                None
        Returns:
        --------
                None
        """
        self.driver.close()

    def download_result_images(self) -> None:
        """
        Download catalof SERP images

        Args:
        -----
                None
        Returns:
        --------
                None
        """
        self.catalog_df["image_file_name"] = range(1, len(self.catalog_df) + 1)

        def process_image_row(row):
            image_path = os.path.join(
                self.image_dir,
                settings.IMAGE_FILE_NAME_FORMAT.format(row["image_file_name"]),
            )
            helper.download_image(row["Image"], image_path)

        self.catalog_df.apply(process_image_row, axis=1)

    def image_similarity_process(self) -> None:
        """
        Compute the image similarity between input image and catalog SERP images
        Args:
        -----
                None
        Returns:
        --------
                None
        """
        comp_logger.info("Downloading Images")
        self.download_result_images()

        comp_logger.info("Computing product image similiarity index")
        image_similarity_helper_obj = ImageSimilarity(
            self.catalog_df, self.image_dir, self.search_image_path
        )
        image_similarity_helper_obj.generate_image_similarity_index()
        self.catalog_df = image_similarity_helper_obj.catalog_df

    def text_similarity_process(self):
        """
        Compute text similarity between input query and catalog serp product names
        Args:
        -----
                None
        Returns:
        --------
                None
        """
        comp_logger.info("Computing product name similarity")
        self.catalog_df = compute_query_catalog_similarity(
            self.catalog_df, self.query, "Name"
        )
        self.catalog_df = self.catalog_df.sort_values(
            by=["TFIDF_COSINE", "Price", "Name"], ascending=[False, True, True]
        )

    def generate_html_response(self) -> None:
        """
        Generate HTML response page for process result

        Args:
        -----
                None
        Returns:
        --------
                None
        """
        comp_logger.info("Generating System Response")
        get_html_from_dataframe(
            self.catalog_df, self.query, self.recommendation_html_file_path
        )
        self.get_html_screenshot()

    def get_html_screenshot(self) -> None:
        """
        Save html response screenshot

        Args:
        -----
                None
        Returns:
        --------
                None
        """
        self.driver.get(
            "file://"
            + os.path.join(settings.BASE_DIR, self.recommendation_html_file_path)
        )
        self.driver.save_screenshot(self.recommendation_html_screenshot)

    def generate_top_n_picks(self):
        """
        Generate the top N recommendations for the given query and image

        Args:
        -----
                None
        Returns:
        --------
                None
        """

        top_n_pricks_list = []
        cnt = 1

        def top_n_picks(row) -> None:
            """
            Append pick to list

            Args:
            -----
                    None
            Returns:
            --------
                    None
            """
            nonlocal cnt
            name = row["Name"]
            url = row["Url"]
            top_n_pricks_list.append(
                f"{cnt}.\t{name}\t\t{url}\n\n".format(cnt, name, url)
            )

            cnt += 1

        self.catalog_df[["Name", "Url"]].iloc[: settings.TOP_N_PICKS].apply(
            top_n_picks, axis=1
        )
        self.top_n_picks_recommendation = "\n".join(top_n_pricks_list)

    def update_project_status(self, status: str, failed_log=None) -> None:
        """
        Update project status
        Args:
        -----
                None
        Returns:
        --------
                None
        """
        if failed_log:
            self.project.failed_log = failed_log
        self.project.status = status
        self.project.save()

    def main(self) -> None:
        """
        Stage of the object method execution
        """
        comp_logger.info(f"For query {self.query} and user {self.user}")
        self.get_marketplace_catalog_df()

        if len(self.catalog_df) > 0:
            self.image_similarity_process()
            self.text_similarity_process()
            self.catalog_df["serp_weightage"] = (
                self.catalog_df["image_similarity_weightage"]
                + self.catalog_df["text_match_weightage"]
            )
            self.catalog_df.sort_values(
                by=["serp_weightage"], ascending=False, inplace=True
            )

            # self.generate_html_response()
            # self.generate_top_n_picks()
            self.save_merged_platformat_file()
            comp_logger.info(f"Process completed for: {self.project_id}")
        else:
            comp_logger.info("No Results")
