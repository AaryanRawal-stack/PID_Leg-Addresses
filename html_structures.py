import requests

# URLs for House, Senate, and OCPF
house_url = "https://malegislature.gov/Legislators/Members/House"
senate_url = "https://malegislature.gov/Legislators/Members/Senate"
ocpf_url = "https://www.ocpf.us/Home/Index"

# Fetch and save the House page HTML
response_house = requests.get(house_url)
with open("house_page.html", "w", encoding="utf-8") as file:
    file.write(response_house.text)

# Fetch and save the Senate page HTML
response_senate = requests.get(senate_url)
with open("senate_page.html", "w", encoding="utf-8") as file:
    file.write(response_senate.text)

# Fetch and save the OCPF page HTML
response_ocpf = requests.get(ocpf_url)
with open("ocpf_page.html", "w", encoding="utf-8") as file:
    file.write(response_ocpf.text)

print("HTML content for House, Senate, and OCPF pages saved successfully!")
