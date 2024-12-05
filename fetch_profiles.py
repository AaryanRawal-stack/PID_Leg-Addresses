import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_profile_and_statement_links(input_csv, output_csv):
    """
    Fetch legislator profile and Organization Statement links, updating the CSV dynamically.
    """
    # Load the data
    data = pd.read_csv(input_csv)
    if 'Profile Page Link' not in data.columns:
        data['Profile Page Link'] = None
    if 'Organization Statement Link' not in data.columns:
        data['Organization Statement Link'] = None

    # Setup Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode
    service = Service('/usr/local/bin/chromedriver')  # Update this path as necessary
    driver = webdriver.Chrome(service=service, options=options)

    for index, row in data.iterrows():
        last_name = row['Last Name']
        search_url = f"https://www.ocpf.us/PublicSearch/Index?q={last_name}"
        logging.info(f"Searching for {last_name} at {search_url}")
        driver.get(search_url)

        profile_url = None
        statement_url = None

        try:
            # Wait for and click the profile link
            profile_link = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href^="/Filers?q="]'))
            )
            profile_url = profile_link.get_attribute('href')
            profile_link.click()

            # Switch to the new tab
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[-1])
            logging.info(f"Switched to profile page. Current URL: {driver.current_url}")

            # Save the profile page link
            data.at[index, 'Profile Page Link'] = profile_url
            data.to_csv(output_csv, index=False)
            logging.info(f"Profile link saved for {last_name}: {profile_url}")

            # Locate the Organization Statement link
            org_statement = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'organizationStatementBlobUrlLink'))
            )
            statement_url = org_statement.get_attribute('href')

            # Save the Organization Statement link
            data.at[index, 'Organization Statement Link'] = statement_url
            data.to_csv(output_csv, index=False)
            logging.info(f"Organization Statement link saved for {last_name}: {statement_url}")

        except Exception as e:
            logging.error(f"Error processing {last_name}: {e}")

        finally:
            # Close the current tab and switch back
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    # Close the browser
    driver.quit()
    logging.info("Browser session closed.")

# Call the function for House and Senate
fetch_profile_and_statement_links('Massachusetts_House_Members.csv', 'Updated_House_Members.csv')
fetch_profile_and_statement_links('Massachusetts_Senate_Members.csv', 'Updated_Senate_Members.csv')
