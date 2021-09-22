"""
Module containing methods to obtain SERP dataframe from
marketplaces
"""

import re
import pandas as pd
from bs4 import BeautifulSoup

from django.conf import settings


def get_amazon_serp_catalog(page_content: str, dataframe_headers: list) -> pd.DataFrame:
    """
    Get Amazon SERP pages results in dataframe

    Args:
    -----
            page_content (str): Page source
            dataframe_headers(list): List containing dataframe column names

    Return:
    -------
            pandas dataframe containing the AMAZON SERP results for given page source
    """
    soup = BeautifulSoup(page_content, "lxml")
    serp_list_items = soup.findAll("div", {"data-asin": re.compile(r"^(?!\s*$).+")})
    serp_list_items_cnt = len(serp_list_items)
    # print(serp_list_items_cnt)

    amazon_catalog_df = pd.DataFrame(columns=dataframe_headers)
    if serp_list_items_cnt > 0:
        for serp_item in serp_list_items:
            try:
                prod_dict = {}
                serp_item_img = serp_item.find("img")["src"]
                prod_dict[dataframe_headers[2]] = serp_item_img

                serp_item_url = f"https://amazon.com{serp_item.find('a')['href']}"
                prod_dict[dataframe_headers[1]] = serp_item_url

                serp_item_name = serp_item.find("h2").text.replace("\n", "")
                prod_dict[dataframe_headers[0]] = serp_item_name

                # #print(serp_item_name)
                serp_price_range = serp_item.findAll("span", {"class": "a-offscreen"})
                if len(serp_price_range) > 0:
                    serp_price_range = list(map(lambda x: x.text, serp_price_range))
                    serp_price = "-".join(serp_price_range)
                else:
                    serp_price = ""
                prod_dict[dataframe_headers[3]] = serp_price
                prod_dict["Platform"] = "Amazon"
                amazon_catalog_df = amazon_catalog_df.append(
                    prod_dict, ignore_index=True
                )

            except:
                continue
    return amazon_catalog_df.iloc[: settings.MAX_SERP_LIST_COUNT]


def get_google_serp_catalog(page_content: str, dataframe_headers: list) -> pd.DataFrame:
    """
    Get Google SERP pages results in dataframe

    Args:
    -----
            page_content (str): Page source
            dataframe_headers(list): List containing dataframe column names

    Return:
    -------
            pandas dataframe containing the Google SERP results for given page source
    """

    soup = BeautifulSoup(page_content, "lxml")

    serp_list_items = soup.findAll("div", {"class": re.compile(r"list-result")})
    serp_list_items_cnt = len(serp_list_items)

    google_catalog_df = pd.DataFrame(columns=dataframe_headers)
    # print(serp_list_items_cnt)

    if serp_list_items_cnt > 0:
        for serp_item in serp_list_items:
            prod_dict = {}
            thumbnail_section = serp_item.find(
                "div", {"class": re.compile(r"thumbnail")}
            )
            serp_item_img = thumbnail_section.find("a").find("img")["src"]
            prod_dict[dataframe_headers[2]] = serp_item_img

            link_aclk_id = serp_item["data-docid"]
            serp_item_url = f"https://www.google.com/shopping/product/1\
            					/specs?prds=pid:{link_aclk_id}"  # spec page url

            prod_dict[dataframe_headers[1]] = serp_item_url

            serp_item_name = thumbnail_section.find_next_sibling("div").find("a").text
            prod_dict[dataframe_headers[0]] = serp_item_name
            serp_price = (
                thumbnail_section.find_next_sibling("div")
                .find("div")
                .find("div")
                .find_next_sibling("div")
                .find("span", {"aria-hidden": "true"})
                .text
            )
            prod_dict[dataframe_headers[3]] = serp_price
            prod_dict["Platform"] = "Google"
            google_catalog_df = google_catalog_df.append(prod_dict, ignore_index=True)

    return google_catalog_df.iloc[: settings.MAX_SERP_LIST_COUNT]


def get_ebay_serp_catalog(page_content: str, dataframe_headers: list) -> pd.DataFrame:
    """
    Get Eay SERP pages results in dataframe

    Args:
    -----
            page_content (str): Page source
            dataframe_headers(list): List containing dataframe column names

    Return:
    -------
            pandas dataframe containing the Ebay SERP results for given page source
    """

    soup = BeautifulSoup(page_content, "lxml")

    # serp_list_items = soup.findAll('li',{"id" : re.compile(r'srp-river-results-listing')})

    try:
        serp_list_items = soup.find(
            "ul", {"class": "srp-results srp-grid clearfix"}
        ).findAll("li", recursive=False)
    except:
        serp_list_items = soup.find(
            "ul", {"class": "srp-results srp-list clearfix"}
        ).findAll("li", recursive=False)

    serp_list_items_cnt = len(serp_list_items)

    ebay_catalog_df = pd.DataFrame(columns=dataframe_headers)
    # print(serp_list_items_cnt)

    if serp_list_items_cnt > 0:
        for serp_item in serp_list_items:
            prod_dict = {}
            thumbnail_section = serp_item.find(
                "div", {"class": re.compile(r"image-section")}
            )
            serp_item_img = thumbnail_section.find("img")["src"]
            prod_dict[dataframe_headers[2]] = serp_item_img

            serp_item_url = thumbnail_section.find("a")["href"]
            prod_dict[dataframe_headers[1]] = serp_item_url

            serp_item_name = serp_item.find("h3").text.replace("SPONSORED", "")
            prod_dict[dataframe_headers[0]] = serp_item_name

            serp_price = serp_item.find("span", {"class": "s-item__price"}).text
            prod_dict[dataframe_headers[3]] = serp_price
            prod_dict["Platform"] = "Ebay"
            ebay_catalog_df = ebay_catalog_df.append(prod_dict, ignore_index=True)

    return ebay_catalog_df.iloc[: settings.MAX_SERP_LIST_COUNT]


def get_walmart_serp_catalog(
    page_content: str, dataframe_headers: list
)-> pd.DataFrame:
    """
    Get Walmart SERP pages results in dataframe

    Args:
    -----
            page_content (str): Page source
            dataframe_headers(list): List containing dataframe column names

    Return:
    -------
            pandas dataframe containing the Walmart SERP results for given page source
    """

    soup = BeautifulSoup(page_content, "lxml")
    serp_list_items = soup.findAll(
        "li", {"data-tl-id": re.compile(r"ProductTileGridView")}
    )
    serp_list_items_cnt = len(serp_list_items)
    serp_list_type = 1

    if serp_list_items_cnt == 0:
        serp_list_items = soup.findAll(
            "div", {"data-tl-id": re.compile(r"ProductTileListView")}
        )
        serp_list_type = 2

    serp_list_items_cnt = len(serp_list_items)

    # print(serp_list_items_cnt)
    # print(serp_list_type)

    walmart_catalog_df = pd.DataFrame(columns=dataframe_headers)
    if serp_list_type == 1:
        # type 1 scrapping
        for serp_item in serp_list_items[: settings.MAX_SERP_LIST_COUNT]:
            prod_dict = {}
            thumbnail_section = serp_item.find(
                "div", {"class": re.compile(r"productimage")}
            )
            serp_item_img = thumbnail_section.find("img")["src"]
            prod_dict[dataframe_headers[2]] = serp_item_img

            serp_item_url = (
                f"https://www.walmart.com{thumbnail_section.find('a')['href']}"
            )
            prod_dict[dataframe_headers[1]] = serp_item_url

            # serp_item_name = serp_item.find('div',{'class':re.compile(r'product-title')})
            # .find('a').text.replace('...','').strip()

            serp_item_title_elem = serp_item.find(
                "div", {"class": re.compile(r"product-title")}
            ).find("a")

            try:
                serp_item_brand = serp_item_title_elem.find(
                    "span", {"class": re.compile(r"product-brand")}
                ).text
            except:
                serp_item_brand = ""

            try:
                serp_item_name = (
                    serp_item_title_elem.find("span").find_next_sibling("span").text
                )
            except:
                serp_item_name = serp_item_title_elem.text.replace("...", "").strip()

            serp_item_name = (serp_item_brand + " " + serp_item_name).strip()

            prod_dict[dataframe_headers[0]] = serp_item_name
            try:
                serp_price = serp_item.find("span", {"class": "price-group"}).text
            except:
                serp_price = ""
            prod_dict[dataframe_headers[3]] = serp_price
            prod_dict["Platform"] = "Walmart"

            walmart_catalog_df = walmart_catalog_df.append(prod_dict, ignore_index=True)

    else:
        # for type 2 scrapping
        for serp_item in serp_list_items:
            prod_dict = {}
            thumbnail_section = serp_item.find(
                "div", {"class": re.compile(r"list-image-wrapper")}
            )
            serp_item_img = thumbnail_section.find("img")["src"]
            prod_dict[dataframe_headers[2]] = serp_item_img

            serp_item_url = (
                f"https://www.walmart.com{thumbnail_section.find('a')['href']}"
            )

            prod_dict[dataframe_headers[1]] = serp_item_url

            serp_item_name = (
                serp_item.find("div", {"class": re.compile(r"product-title")})
                .find("a")
                .text.replace("...", "")
                .strip()
            )
            prod_dict[dataframe_headers[0]] = serp_item_name

            try:
                serp_price = serp_item.find("span", {"class": "price-group"}).text
            except:
                serp_price = ""
            prod_dict[dataframe_headers[3]] = serp_price
            prod_dict["Platform"] = "Walmart"
            walmart_catalog_df = walmart_catalog_df.append(prod_dict, ignore_index=True)

    return walmart_catalog_df.iloc[: settings.MAX_SERP_LIST_COUNT]
