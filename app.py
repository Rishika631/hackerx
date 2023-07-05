import requests
import streamlit as st

API_URL = 'https://healthapi.dev/api'

# Function to fetch information about a specific medicine
def fetch_medicine_info(medicine_name):
    url = f'{API_URL}/medications?name={medicine_name}'
    response = requests.get(url)
    data = response.json()
    return data

# Function to fetch information about a specific disease
def fetch_disease_info(disease_name):
    url = f'{API_URL}/diseases?name={disease_name}'
    response = requests.get(url)
    data = response.json()
    return data

# Streamlit app
def main():
    st.title("Health Bot")
    option = st.sidebar.selectbox("Select an option:", ("Medicine", "Disease"))

    if option == "Medicine":
        st.write("Enter a medicine name to fetch information:")
        medicine_name = st.text_input("Medicine Name")

        if st.button("Fetch Information"):
            data = fetch_medicine_info(medicine_name)

            if 'error' in data:
                st.write(f"Error: {data['error']}")
            else:
                st.write("### Medicine Information")
                st.write(f"Name: {data['name']}")
                st.write(f"Description: {data['description']}")
                st.write(f"Usage: {data['usage']}")
                st.write(f"Precautions: {data['precautions']}")
                st.write(f"Side Effects: {data['side_effects']}")
                st.write(f"Contraindications: {data['contraindications']}")

    elif option == "Disease":
        st.write("Enter a disease name to fetch information:")
        disease_name = st.text_input("Disease Name")

        if st.button("Fetch Information"):
            data = fetch_disease_info(disease_name)

            if 'error' in data:
                st.write(f"Error: {data['error']}")
            else:
                st.write("### Disease Information")
                st.write(f"Name: {data['name']}")
                st.write(f"Description: {data['description']}")
                st.write(f"Symptoms: {', '.join(data['symptoms'])}")
                st.write(f"Treatments: {', '.join(data['treatments'])}")

if __name__ == '__main__':
    main()
