import streamlit as st
import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import Spider, Request


def scrape_mayo_clinic(query):
    url = f"https://www.mayoclinic.org/search/search-results?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Process and extract relevant information from the webpage
    # Return the response to be shown to the user


class WebmdSpider(Spider):
    name = "webmd"
    allowed_domains = ['webmd.com']
    start_urls = []

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://www.webmd.com/drugs/2/search?type=name&query={query}']

    def parse(self, response):
        drug_list = response.xpath('//ul[@class="search-list"]/li/a[@class="search-link"]')
        for drug in drug_list:
            yield Request(response.urljoin(drug.xpath("@href").extract_first()), callback=self.parse_details)

    def parse_details(self, response):
        name = response.xpath('//h1/text()').extract_first()
        uses = ' '.join(response.xpath('//h2[contains(text(), "Uses")]/following-sibling::div//text()').extract())
        how_to_use = ' '.join(response.xpath('//h2[contains(text(), "How to Use")]/following-sibling::div//text()').extract())
        side_effects = ' '.join(response.xpath('//h2[contains(text(), "Side Effects")]/following-sibling::div//text()').extract())
        precautions = ' '.join(response.xpath('//h2[contains(text(), "Precautions")]/following-sibling::div//text()').extract())
        interactions = ' '.join(response.xpath('//h2[contains(text(), "Interactions")]/following-sibling::div//text()').extract())

        result = f"Name: {name}\n\n" \
                 f"Uses: {uses}\n\n" \
                 f"How to Use: {how_to_use}\n\n" \
                 f"Side Effects: {side_effects}\n\n" \
                 f"Precautions: {precautions}\n\n" \
                 f"Interactions: {interactions}\n\n"

        st.write(result)


def scrape_webmd(query):
    process = CrawlerProcess(get_project_settings())
    process.crawl(WebmdSpider, query=query)
    process.start()


def get_answer(query, sources):
    if "Mayo Clinic" in sources:
        scrape_mayo_clinic(query)

    if "WebMD" in sources:
        scrape_webmd(query)


def main():
    st.title("Medical Chatbot")
    query = st.text_input("Ask a medical question")

    if st.button("Search"):
        selected_sources = st.multiselect("Select sources", ["Mayo Clinic", "WebMD"])
        get_answer(query, selected_sources)


if __name__ == "__main__":
    main()
