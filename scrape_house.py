import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_house_members():
    # Load the HTML file
    with open("house_page.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Locate the table
    table = soup.find("table", {"id": "legislatorTable"})
    rows = table.find_all("tr")[1:]  # Skip the header row

    legislators = []
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 8:  # Ensure there are enough columns
            try:
                first_name = columns[2].find("a").text.strip()
                last_name = columns[3].find("a").text.strip()
                district = columns[4].text.strip()
                party = columns[5].text.strip()
                room_number = columns[6].text.strip() if len(columns) > 6 else "N/A"
                phone_number = columns[7].text.strip() if len(columns) > 7 else "N/A"
                email = (
                    columns[8].find("a")["href"].replace("mailto:", "").strip()
                    if columns[8].find("a")
                    else "N/A"
                )

                legislators.append({
                    "First Name": first_name,
                    "Last Name": last_name,
                    "District": district,
                    "Party": party,
                    "Room Number": room_number,
                    "Phone Number": phone_number,
                    "Email": email,
                })
            except Exception as e:
                print(f"Error parsing row: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(legislators)
    return df


# Scrape and save to a CSV file
df = scrape_house_members()
df.to_csv("Massachusetts_House_Members.csv", index=False)
print("Data has been saved to 'Massachusetts_House_Members.csv'")
