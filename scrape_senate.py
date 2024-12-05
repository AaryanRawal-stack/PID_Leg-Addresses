import pandas as pd
from bs4 import BeautifulSoup

def scrape_senate_members():
    # Load the Senate HTML file
    with open("senate_page.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    
    # Find the table containing legislator information
    table = soup.find("table", {"id": "legislatorTable"})
    rows = table.find_all("tr")[1:]  # Skip the header row

    senators = []
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 8:  # Ensure there are enough columns
            try:
                first_name = columns[2].find("a").text.strip()
                last_name = columns[3].find("a").text.strip()
                district = columns[4].text.strip()
                party = columns[5].text.strip()
                room = columns[6].text.strip() if len(columns) > 6 else "N/A"
                phone = columns[7].text.strip() if len(columns) > 7 else "N/A"
                email = (
                    columns[8].find("a")["href"].replace("mailto:", "").strip()
                    if columns[8].find("a")
                    else "N/A"
                )
                
                senators.append({
                    "First Name": first_name,
                    "Last Name": last_name,
                    "District": district,
                    "Party": party,
                    "Room": room,
                    "Phone": phone,
                    "Email": email,
                })
            except Exception as e:
                print(f"Error parsing row: {e}")
    
    # Convert to DataFrame
    return pd.DataFrame(senators)


# Scrape and save to a CSV file
senate_df = scrape_senate_members()
senate_df.to_csv("Massachusetts_Senate_Members.csv", index=False)
print("Data has been saved to 'Massachusetts_Senate_Members.csv'")
