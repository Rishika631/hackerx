import requests
import streamlit as st

API_ENDPOINT = 'https://mcc.api.mayo.edu/semantic/v2/ask'

def fetch_mayo_clinic_information(query):
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'question': query,
        'target': 'web'
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    data = response.json()
    return data

def main():
    st.title("Health Bot")
    st.write("Enter a health-related question:")

    question = st.text_input("Question")

    if st.button("Fetch Information"):
        data = fetch_mayo_clinic_information(question)

        if 'answers' in data and len(data['answers']) > 0:
            answer = data['answers'][0]
            st.write("### Health Information")
            st.write(f"Question: {question}")
            st.write(f"Answer: {answer['content']}")
        else:
            st.write("No information found for the given question.")

if __name__ == '__main__':
    main()
