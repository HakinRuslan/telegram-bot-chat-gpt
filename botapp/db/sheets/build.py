import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)


sheet_user = client.open("users_table_1").worksheet("users_table_1")
sheet_apl = client.open("apl_table_1").worksheet("apl_table_1")