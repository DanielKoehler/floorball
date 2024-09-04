import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import pytz

# URL of the page
url = "http://statistik.innebandy.se/ft.aspx?scr=fixturelist&ftid=37792"

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Create a new calendar
cal = Calendar()

# Find the table with the match schedule
table = soup.find_all("table", {"class": "clCommonGrid"})[1]  # The second table contains the match schedule
rows = table.find_all("tr")[2:]  # Skip the first two header rows

# Set the time zones
gmt = pytz.timezone('GMT')
cet = pytz.timezone('CET')

# Loop through the rows and extract event details
for row in rows:

    if "clBold" in row.get("class", []):  # Skip rows that are just group headers (Omgång X)
        continue
    
    columns = row.find_all("td")
    if len(columns) < 6:  # Skip rows that don't have enough columns
        continue
    
    date_str = columns[0].get_text()
    match_details = columns[2].get_text(strip=True)
    venue = columns[5].get_text(strip=True)

    if "Marieberg" not in match_details: 
        continue

    # Parse date and time
    try:
        # Assume the time is initially in GMT
        event_datetime = gmt.localize(datetime.strptime(date_str, "%Y-%m-%d %H:%M"))
        # Convert to CET
        event_datetime_cet = event_datetime.astimezone(cet)
    except ValueError:
        print("Skipping row with invalid date format:", date_str)
        continue  # Skip row if the date format doesn't match

    # Create an event
    event = Event()
    event.name = match_details
    event.begin = event_datetime_cet
    event.location = venue

    print(f"Added event: {event.name} at {event.begin} ({event.location})")

    # Add event to calendar
    cal.events.add(event)

# Save the calendar to an .ics file
with open("innebandy_schedule.ics", "w") as f:
    f.writelines(cal)

print("iCal file created successfully.")
