import streamlit as st
import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def scrape_mayo_clinic(query):
    url = f"https://www.mayoclinic.org/search/search-results?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Process and extract relevant information from the webpage
    # Return the response to be shown to the user

# Function to scrape WebMD using the Spider
def scrape_webmd(query):
    # Create a CrawlerProcess and get the settings
    process = CrawlerProcess(get_project_settings())

    # Start the spider and pass the query as an argument
    process.crawl(spiders/webmd_spider.py, query=query)
    process.start()


def get_answer(query, sources):
    answers = []
    
    if "Mayo Clinic" in sources:
        answers.extend(scrape_mayo_clinic(query))
    
    if "WebMD" in sources:
        answers.extend(scrape_webmd(query))
    
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
