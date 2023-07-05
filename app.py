import requests
import streamlit as st

# Function to fetch health information from FAERS API
def fetch_health_information(question):
    url = f"https://api.fda.gov/drug/event.json?limit=1&search={question}"
    response = requests.get(url)
    data = response.json()
    return data

# Streamlit app
def main():
    st.title("Health Bot")
    st.write("Enter a question to fetch health-related information:")

    # User input for question
    question = st.text_input("Question")

    if st.button("Fetch Information"):
        # Fetch health information
        data = fetch_health_information(question)

        # Display results
        if 'results' in data and len(data['results']) > 0:
            event_info = data['results'][0]
            st.write("### Health Information")
            st.write(f"Question: {question}")
            st.write(f"Event Date: {event_info.get('receivedate', 'N/A')}")
            st.write(f"Event Type: {event_info.get('primarysource', {}).get('report_type', 'N/A')}")
            st.write(f"Patient Age: {event_info.get('patient', {}).get('patientage', 'N/A')}")
            st.write(f"Patient Sex: {event_info.get('patient', {}).get('patientsex', 'N/A')}")
            st.write(f"Description: {event_info.get('patient', {}).get('reaction', ['N/A'])[0].get('reactionmeddrapt', 'N/A')}")
        else:
            st.write("No information found for the given question.")

if __name__ == '__main__':
    main()
