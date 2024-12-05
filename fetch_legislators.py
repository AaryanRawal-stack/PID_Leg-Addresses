from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup Selenium
options = Options()
options.headless = False  # Set to True to run Chrome in the background
service = Service('/usr/local/bin/chromedriver')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=options)

def preprocess_address(address):
    """
    Preprocess the address to remove second lines and format ZIP codes to 5 digits.
    """
    # Use regex to extract valid components
    match = re.match(r"(.*?)(?:,|#).*?(\b[A-Z][a-zA-Z]+),\s*(MA\s+\d{5})", address)
    if match:
        street_address = match.group(1).strip()  # The part before any commas or hashes
        city = match.group(2).strip()  # The valid city
        zip_code = match.group(3).strip().split()[-1][:5]  # Ensure ZIP is 5 digits
        return street_address, city, zip_code

    logging.warning(f"Address preprocessing failed for: {address}")
    return None, None, None

def fetch_legislators(address, city, zipcode):
    """
    Fetch the state representative and senator names based on the address, city, and ZIP code.
    """
    try:
        logging.info(f"Processing address: {address}, city: {city}, ZIP: {zipcode}")
        # Navigate to Find My Legislator page
        driver.get("https://malegislature.gov/Search/FindMyLegislator")
        logging.info("Navigated to Find My Legislator page.")

        # Enter street address
        address_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Address")))
        address_input.clear()
        address_input.send_keys(address)
        logging.info("Entered street address.")

        # Enter city
        city_input = driver.find_element(By.ID, "City")
        city_input.clear()
        city_input.send_keys(city)
        logging.info("Entered city.")

        # Enter ZIP code
        zip_input = driver.find_element(By.ID, "ZipCode")
        zip_input.clear()
        zip_input.send_keys(zipcode)
        logging.info("Entered ZIP code.")

        # Click the Search button
        search_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-lg.fnStart")
        search_button.click()
        logging.info("Clicked the Search button.")
        time.sleep(5)  # Wait for results to load

        # Extract Representative's name
        try:
            rep_name = driver.find_element(By.XPATH, "//h3[text()='Representative']/following-sibling::a/strong").text
            logging.info(f"Found Representative: {rep_name}")
        except:
            rep_name = "Not Found"
            logging.warning("State Representative not found.")

        # Extract Senator's name
        try:
            sen_name = driver.find_element(By.XPATH, "//h3[text()='Senator']/following-sibling::a/strong").text
            logging.info(f"Found Senator: {sen_name}")
        except:
            sen_name = "Not Found"
            logging.warning("State Senator not found.")

        return rep_name, sen_name

    except Exception as e:
        logging.error(f"Error fetching legislators for {address}, {city}, {zipcode}: {e}")
        return "Error", "Error"

def process_file(file_name):
    """
    Process a file to fetch legislators for each address.
    """
    data = pd.read_csv(file_name)
    if "State Representative" not in data.columns:
        data["State Representative"] = ""
    if "State Senator" not in data.columns:
        data["State Senator"] = ""

    for index, row in data.iterrows():
        address = row.get("Candidate Address")
        if pd.isna(address):
            logging.info(f"Skipping row {index + 1}: No address available.")
            continue

        # Preprocess the address
        street_address, city, zip_code = preprocess_address(address)
        if not street_address or not city or not zip_code:
            logging.warning(f"Skipping row {index + 1}: Failed to preprocess address: {address}")
            continue

        # Skip rows with valid data
        if row.get("State Representative") not in [None, "", "Not Found"] and row.get("State Senator") not in [None, "", "Not Found"]:
            logging.info(f"Skipping row {index + 1}: Legislator data already valid.")
            continue

        # Fetch legislators
        rep_name, sen_name = fetch_legislators(street_address, city, zip_code)

        # Update the DataFrame
        data.at[index, "State Representative"] = rep_name
        data.at[index, "State Senator"] = sen_name
        logging.info(f"Updated row {index + 1} with legislators.")

    # Save back to the same file
    data.to_csv(file_name, index=False)
    logging.info(f"Updated data saved to {file_name}.")

# Process both house and senate files
process_file("Updated_House_Members.csv")
process_file("Updated_Senate_Members.csv")

# Close the browser
driver.quit()
logging.info("Browser session closed.")
