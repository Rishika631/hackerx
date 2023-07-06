import requests
import streamlit as st

MAYO_API_ENDPOINT = 'https://mcc.api.mayo.edu/semantic/v2/ask'
WEBMD_API_ENDPOINT = 'https://www.webmd.com/'

def fetch_mayo_clinic_information(query):
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'question': query,
        'target': 'web'
    }

    response = requests.post(MAYO_API_ENDPOINT, headers=headers, json=data)
    data = response.json()
    return data

def fetch_webmd_information(query):
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'question': query,
        'target': 'web'
    }

    response = requests.post(WEBMD_API_ENDPOINT, headers=headers, json=data)
    data = response.json()
    return data

def main():
    st.title("Health Bot")
    st.write("Enter a health-related question:")

    question = st.text_input("Question")

    if st.button("Fetch Information"):
        mayo_data = fetch_mayo_clinic_information(question)
        webmd_data = fetch_webmd_information(question)

        st.write("### Mayo Clinic Information")
        if 'answers' in mayo_data and len(mayo_data['answers']) > 0:
            answer = mayo_data['answers'][0]
            st.write(f"Question: {question}")
            st.write(f"Answer: {answer['content']}")
        else:
            st.write("No information found from Mayo Clinic API.")

        st.write("### WebMD Information")
        if 'data' in webmd_data and 'article' in webmd_data['data']:
            article = webmd_data['data']['article']
            st.write(f"Title: {article['title']}")
            st.write(f"Summary: {article['summary']}")
        else:
            st.write("No information found from WebMD API.")

if __name__ == '__main__':
    main()
