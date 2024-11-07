import json
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope and authenticate with the service account
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
json_key = json.loads(os.getenv("GKEY"), strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(credentials)

# Open the Google Sheet by name
spreadsheet = client.open("Team 7 Data")
worksheet = spreadsheet.sheet1  # Access the first sheet


# Function to insert the JSON string into the first column
def submit_json_to_sheets(json_data):
    # Convert JSON data to string format
    json_string = json.dumps(json_data)
    # Append the JSON string as a new row with one cell in the first column
    worksheet.append_row([json_string])
