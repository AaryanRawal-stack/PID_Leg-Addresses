import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define URLs
house_url = "https://malegislature.gov/Legislators/Members/House"
senate_url = "https://malegislature.gov/Legislators/Members/Senate"
ocpf_url = "https://www.ocpf.us/Home/Index"

# Setup Selenium for OCPF search
options = Options()
options.headless = True
service = Service('/path/to/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

# Ensure a folder for PDFs and images
os.makedirs('./temp', exist_ok=True)
os.makedirs('./temp/images', exist_ok=True)

# Function to scrape legislator data
def scrape_legislators(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    legislators = []
    for legislator in soup.select('.row-legislator'):
        name = legislator.select_one('.legislator-name').text.strip()
        district = legislator.select_one('.legislator-district').text.strip()
        party = legislator.select_one('.legislator-party').text.strip()
        first_name, last_name = name.split(' ', 1)
        legislators.append({
            'First Name': first_name,
            'Last Name': last_name,
            'District': district,
            'Party': party
        })
    return legislators

# Function to perform OCR on a PDF
def ocr_pdf(pdf_path):
    text = ""
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        image_path = f"./temp/images/page_{i + 1}.png"
        image.save(image_path, 'PNG')
        text += pytesseract.image_to_string(image_path)
    return text

# Function to fetch address from OCPF
def fetch_address(last_name):
    driver.get(ocpf_url)
    search_box = driver.find_element(By.ID, 'search-box')
    search_box.send_keys(last_name)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)
    try:
        profile_link = driver.find_element(By.CSS_SELECTOR, '.search-result a')
        profile_link.click()
        time.sleep(2)
        pdf_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'Organization Statement')
        pdf_url = pdf_link.get_attribute('href')
        pdf_path = f"./temp/{last_name}.pdf"
        
        # Download the PDF
        response = requests.get(pdf_url)
        with open(pdf_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Downloaded PDF for {last_name}")

        # Extract address
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if "Residential Address:" in text:
                        address_line = text.split("Residential Address:")[1].split("\n")[0]
                        logging.info(f"Found address for {last_name}: {address_line.strip()}")
                        return address_line.strip()
        except Exception:
            logging.warning(f"Failed to extract text from PDF for {last_name}. Using OCR...")
            text = ocr_pdf(pdf_path)
            if "Residential Address:" in text:
                address_line = text.split("Residential Address:")[1].split("\n")[0]
                logging.info(f"Found address for {last_name} using OCR: {address_line.strip()}")
                return address_line.strip()
    except Exception as e:
        logging.error(f"Error fetching address for {last_name}: {e}")
    return None

# Scrape House and Senate members
logging.info("Scraping House members...")
house_legislators = scrape_legislators(house_url)
logging.info("Scraping Senate members...")
senate_legislators = scrape_legislators(senate_url)

# Create DataFrames
house_df = pd.DataFrame(house_legislators)
senate_df = pd.DataFrame(senate_legislators)

# Load or create spreadsheet
output_file = 'Massachusetts_Legislators.xlsx'
if os.path.exists(output_file):
    writer = pd.ExcelWriter(output_file, mode='a', if_sheet_exists='overlay')
else:
    writer = pd.ExcelWriter(output_file, mode='w')

# Add residential addresses dynamically
house_df['Residential Address'] = house_df['Last Name'].apply(lambda x: fetch_address(x) or "Not Found")
senate_df['Residential Address'] = senate_df['Last Name'].apply(lambda x: fetch_address(x) or "Not Found")

# Save progress to Excel after processing each legislator
logging.info("Saving data to Excel...")
house_df.to_excel(writer, sheet_name='Representatives', index=False)
senate_df.to_excel(writer, sheet_name='Senators', index=False)
writer.close()

# Cleanup
driver.quit()
logging.info("All tasks completed successfully.")
