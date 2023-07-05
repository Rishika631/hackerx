import requests
import streamlit as st

# Function to fetch drug information from OpenFDA API
def fetch_drug_information(drug_name):
    url = f'https://api.fda.gov/drug/label.json?search=brand_name:{drug_name}'
    response = requests.get(url)
    data = response.json()
    return data

# Streamlit app
def main():
    st.title("Health Bot")
    st.write("Enter a drug name to fetch information:")

    # User input for drug name
    drug_name = st.text_input("Drug Name")

    if st.button("Fetch Information"):
        # Fetch drug information
        data = fetch_drug_information(drug_name)

        # Display results
        if 'results' in data and len(data['results']) > 0:
            drug_info = data['results'][0]
            st.write("### Drug Information")
            st.write(f"Brand Name: {drug_info.get('openfda', {}).get('brand_name', ['N/A'])[0]}")
            st.write(f"Generic Name: {drug_info.get('openfda', {}).get('generic_name', ['N/A'])[0]}")
            st.write(f"Manufacturer: {drug_info.get('openfda', {}).get('manufacturer_name', ['N/A'])[0]}")
            st.write(f"Indications and Usage: {drug_info.get('indications_and_usage', 'N/A')}")
        else:
            st.write("No information found for the given drug.")

if __name__ == '__main__':
    main()
