import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Selenium Setup
options = Options()
options.headless = True  # Run in headless mode
service = Service('/usr/local/bin/chromedriver')  # Update with the path to your ChromeDriver
driver = webdriver.Chrome(service=service, options=options)

# Input files
input_files = ['Updated_House_Members.csv', 'Updated_Senate_Members.csv']

def fetch_candidate_address(profile_url):
    """
    Fetch the candidate address from the given profile URL.
    """
    try:
        driver.get(profile_url)
        logging.info(f"Navigated to {profile_url}")
        
        # Add a delay to ensure the page fully loads
        time.sleep(5)
        
        # Wait for the Candidate Address element to load
        candidate_address = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-field="candidateFullAddress"]'))
        ).text
        logging.info(f"Found Candidate Address: {candidate_address}")
        return candidate_address
    except Exception as e:
        logging.error(f"Error fetching candidate address: {e}")
        return "Address Not Found"

# Process each file
for input_file in input_files:
    logging.info(f"Processing file: {input_file}")
    data = pd.read_csv(input_file)

    # Add a new column for Candidate Address if not already present
    if 'Candidate Address' not in data.columns:
        data['Candidate Address'] = ""

    # Iterate through each row in the data
    for index, row in data.iterrows():
        profile_url = row['Profile Page Link']  # Assumes the column name is 'Profile Page Link'
        if pd.notna(profile_url):  # Check if URL is valid
            logging.info(f"Processing row {index + 1}/{len(data)}: {profile_url}")
            address = fetch_candidate_address(profile_url)
            data.at[index, 'Candidate Address'] = address  # Update the data in the new column

    # Save the updated spreadsheet
    data.to_csv(input_file, index=False)
    logging.info(f"Updated spreadsheet saved to {input_file}")

# Quit the browser
driver.quit()
logging.info("Browser session closed.")
