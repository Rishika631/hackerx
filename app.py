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
        
        # Return the extracted information
        result = f"Name: {drug_name}\n\n" \
                 f"Uses: {uses}\n\n" \
                 f"Side Effects: {side_effects}\n\n"
        return result
    else:
        return "No results found"



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
    result = ""
    
    if "Mayo Clinic" in sources:
        result += scrape_mayo_clinic(query)
    
    if "WebMD" in sources:
        process = CrawlerProcess(get_project_settings())
        process.crawl(WebmdSpider, query=query)
        process.start()

    return result


def main():
    st.title("Medical Chatbot")
    query = st.text_input("Ask a medical question")

    if st.button("Search"):
        selected_sources = st.multiselect("Select sources", ["Mayo Clinic", "WebMD"])
        result = get_answer(query, selected_sources)
        st.write(result)


if __name__ == "__main__":
    main()
