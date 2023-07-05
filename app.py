import streamlit as st
import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import Spider, Request
from scrapy.selector import Selector


def scrape_mayo_clinic(query):
    url = f"https://www.mayoclinic.org/search/search-results?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Process and extract relevant information from the webpage
    # Return the response to be shown to the user

# Function to scrape WebMD using the Spider
class WebmdSpider(Spider):
    name = "webmd"
    allowed_urls = ['http://www.webmd.com/']
    start_urls = ['http://www.webmd.com/drugs/2/index']

    def parse(self, response):
        atoz = response.xpath('//ul[@class="browse-letters squares"]')[0].xpath("li/a/@href").extract()
        for i in range(len(atoz)):
            yield Request(response.urljoin(atoz[i]), callback=self.parse_sub, dont_filter=True)

    def parse_sub(self, response):
        sub = response.xpath('//ul[@class="browse-subletters squares"]')[0].xpath("li/a/@href").extract()
        for i in range(len(sub)):
            yield Request(response.urljoin(sub[i]), callback=self.parse_drug, dont_filter=True)

    def parse_drug(self, response):
        drug_list = response.xpath('//ul[@class="drug-list"]')[0].xpath("li/a")
        for i in range(len(drug_list)):
            yield Request(response.urljoin(drug_list[i].xpath("@href")[0].extract()), callback=self.parse_details, dont_filter=True)

    def parse_details(self, response):
        Use = ' '.join(response.xpath('//h3[contains(text(), "Uses")]/following-sibling::p//text()').extract())
        HowtoUse = ' '.join(response.xpath('//h3[contains(text(), "How to use")]/following-sibling::p//text()').extract())
        Sides = ' '.join(response.xpath('//h3[contains(text(), "Side Effects")]/following-sibling::div/p//text()').extract()).replace('\r\n', '')
        Precautions = ' '.join(response.xpath('//h3[contains(text(), "Precautions")]/following-sibling::div/p//text()').extract())
        Interactions = ' '.join(response.xpath('//h3[contains(text(), "Interactions")]/following-sibling::div/p//text()').extract())

        # Clean up the extracted data
        Use = Use.strip() if Use else ''
        HowtoUse = HowtoUse.strip() if HowtoUse else ''
        Sides = Sides.strip() if Sides else ''
        Precautions = Precautions.strip() if Precautions else ''
        Interactions = Interactions.strip() if Interactions else ''

        # Create a dictionary with the extracted data
        drug_data = {
            'Use': Use,
            'HowtoUse': HowtoUse,
            'Sides': Sides,
            'Precautions': Precautions,
            'Interactions': Interactions
        }

        yield drug_data



def get_answer(query, sources):
    answers = []

    if "Mayo Clinic" in sources:
        answers.extend(scrape_mayo_clinic(query))

    if "WebMD" in sources:
        # Create a CrawlerProcess and get the settings
        process = CrawlerProcess(get_project_settings())

        # Create a list to store the scraped data
        scraped_data = []

        # Create a callback function to handle the scraped data
        def handle_data(item, response, spider):
            scraped_data.append(item)

        # Start the spider and pass the query as an argument
        process.crawl(WebmdSpider, query=query)
        process.crawl(WebmdSpider, query=query, handle_data=handle_data)
        process.start()

        # Process the scraped data and add it to the answers list
        for item in scraped_data:
            answer = f"Use: {item['Use']}\n\n" \
                     f"How to Use: {item['HowtoUse']}\n\n" \
                     f"Side Effects: {item['Sides']}\n\n" \
                     f"Precautions: {item['Precautions']}\n\n" \
                     f"Interactions: {item['Interactions']}\n\n"
            answers.append(answer)

    # Implement logic to select the best answer based on relevance or any other criteria

    return answers

def main():
    st.title("Medical Chatbot")
    query = st.text_input("Ask a medical question")

    if st.button("Search"):
        # Perform question answering based on the selected sources
        selected_sources = st.multiselect("Select sources", ["Mayo Clinic", "WebMD"])
        answers = get_answer(query, selected_sources)

        # Display the answers
        if answers:
            for answer in answers:
                st.write(answer)
        else:
            st.write("No relevant answers found.")

if __name__ == "__main__":
    main()
