import gspread
import os
import json
from dotenv import load_dotenv

#load sheet
load_dotenv()
SHEET_NAME = os.getenv('SHEET_NAME')

class SheetManager:
   def __init__(self):
        google_creds_raw = os.getenv('GOOGLE_CREDS_JSON')

        if google_creds_raw:
            # Parse the string into a dictionary
            creds_dict = json.loads(google_creds_raw)
            self.gc = gspread.service_account_from_dict(creds_dict)
        else:
            self.gc = gspread.service_account(filename='service_account.json')

        # Open the specific sheet
        self.sh = self.gc.open(SHEET_NAME).sheet1

    def sync_player(self, row_data):
        #get the list of values
        #discord ID
        userID = str(row_data[0])  

        try:
            #check if player already signed up
            cell = self.sh.find(userID, in_column=1)

            if cell:
                #if already there, update
                self.sh.update(f'A{cell.row}:G{cell.row}', [row_data])
                return "updated"
            
            else:
                #if not there, add to sheet
                self.sh.append_row(row_data)
                return "added"
            
        except Exception as e:
            print(f"Connection Error: {e}")
            return "error"
        

    def search_players(self, search_term):
    
        all_records = self.sh.get_all_records()
        
        results = []
        search_term = search_term.lower().strip()

        for row in all_records:

            match_found = (
                search_term in str(row.get('Main Role', '')).lower() or
                search_term in str(row.get('Other Roles', '')).lower() or
                search_term in str(row.get('Main', '')).lower() or
                search_term in str(row.get('Other Characters', '')).lower()
            )

            if match_found:
                results.append(row)
        
        return results
    
    #for when a person has a team or decides they dont want to play
    def delete_player(self, user_id):
        try:
            cell = self.sh.find(str(user_id), in_column=1)
            if cell:
                self.sh.delete_rows(cell.row)
                return True
            return False
        except Exception as e:
            print(f"Delete Error: {e}")
            return False

db = SheetManager()





