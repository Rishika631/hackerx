import streamlit as st
import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import Spider, Request
from webmd.items import WebmdItem
from scrapy import Spider, Request
from scrapy.selector import Selector
import urllib
import re
import html

headers = {'User-Agent': 'Chrome/60.0.3112.113', 
           'enc_data': 'OXYIMo2UzzqFUzYszFv4lWP6aDP0r+h4AOC2fYVQIl8=', 
           'timestamp': 'Mon, 04 Sept 2017 04:35:00 GMT', 
           'client_id': '3454df96-c7a5-47bb-a74e-890fb3c30a0d'}

import streamlit as st
import requests
from bs4 import BeautifulSoup

def scrape_mayo_clinic(query):
    url = f"https://www.mayoclinic.org/search/search-results?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Process and extract relevant information from the webpage
    search_results = soup.find_all("li", class_="search")

    if search_results:
        # Extract the first search result
        first_result = search_results[0]

        # Get the link to the detailed page
        link = first_result.find("a")["href"]

        # Retrieve the detailed page content
        detailed_response = requests.get(link)
        detailed_soup = BeautifulSoup(detailed_response.content, "html.parser")

        # Extract relevant information from the detailed page
        drug_name = detailed_soup.find("h1", class_="drug-name-title").text.strip()
        uses = detailed_soup.find("section", class_="drug-section drug-section-uses").text.strip()
        side_effects = detailed_soup.find("section", class_="drug-section drug-section-side-effects").text.strip()

        # Prepare the result
        result = f"Name: {drug_name}\n\n" \
                 f"Uses: {uses}\n\n" \
                 f"Side Effects: {side_effects}\n\n"

        # Write the result to Streamlit
        st.write(result)
    else:
        st.write("No results found")

# Streamlit app
def main():
    st.title("Web Scraping with Streamlit")
    query = st.text_input("Enter a drug name:")
    if st.button("Scrape"):
        scrape_mayo_clinic(query)

if __name__ == "__main__":
    main()




