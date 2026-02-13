import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any

class SheetHandler:
    def __init__(self, credentials_path: str = None, credentials_dict: Dict[str, Any] = None):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        if credentials_dict:
            self.creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, self.scope)
        else:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = None

    def connect(self, sheet_url: str, worksheet_name: str = None):
        """Connects to a specific spreadsheet and worksheet."""
        try:
            spreadsheet = self.client.open_by_url(sheet_url)
            if worksheet_name:
                self.sheet = spreadsheet.worksheet(worksheet_name)
            else:
                self.sheet = spreadsheet.sheet1
            print(f"Connected to sheet: {spreadsheet.title}")
        except Exception as e:
            print(f"Error connecting to sheet: {e}")
            raise

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Retrieves rows where Status (Col A) is empty or specific value.
        Assumes headers are in the first row.
        """
        all_records = self.sheet.get_all_records()
        pending = []
        # Enumerate to keep track of row index (1-based for gspread update)
        # get_all_records returns a list of dictionaries. 
        # The row index in sheet is i + 2 (1 for header, 1 for 0-index offset)
        for i, record in enumerate(all_records):
            # Check if 'Status' is empty or 'Ready' (adjust based on user pref)
            # User request: A=Status, B=MainKW.
            # We assume header names: Status, MainKW, SubKW1, SubKW2, Goal, SiteName, Slug, DraftURL, ImagePrompts
            status = str(record.get('Status', '')).strip()
            # Allow various "pending" statuses
            allowed_statuses = ['', '未着手', ',', '待機中', '指示待ち']
            if status in allowed_statuses:
                task = record.copy()
                task['row_index'] = i + 2
                pending.append(task)
        return pending

    def update_task_complete(self, row_index: int, draft_url: str, image_prompts: str, title: str = "", description: str = "", html_content: str = ""):
        """Updates the row with completion status and details."""
        # Col A(1)=Status, H(8)=DraftURL, I(9)=ImagePrompts
        # New: J(10)=Title, K(11)=Description, L(12)=Content
        try:
            # Preparing a batch update could be more efficient, but checking types first
            cells = [
                gspread.Cell(row_index, 1, "完了"),
                gspread.Cell(row_index, 8, draft_url),
                gspread.Cell(row_index, 9, image_prompts),
                gspread.Cell(row_index, 10, title),
                gspread.Cell(row_index, 11, description),
                gspread.Cell(row_index, 12, html_content) # Content is usually large
            ]
            # Use update_cells if possible, but standard gspread usage:
            self.sheet.update_cell(row_index, 1, "完了")
            self.sheet.update_cell(row_index, 8, draft_url)
            self.sheet.update_cell(row_index, 9, image_prompts)
            self.sheet.update_cell(row_index, 10, title)
            self.sheet.update_cell(row_index, 11, description)
            if len(html_content) > 49000:
                print(f"Warning: Content length {len(html_content)} may exceed cell limit.")
            self.sheet.update_cell(row_index, 12, html_content)

            print(f"Updated row {row_index} as Complete.")
        except Exception as e:
            print(f"Error updating row {row_index}: {e}")

    def update_status(self, row_index: int, status: str):
        """Updates just the status column."""
        try:
            self.sheet.update_cell(row_index, 1, status)
        except Exception as e:
            print(f"Error updating status for row {row_index}: {e}")

    def get_prompts_from_tab(self, tab_name: str) -> Dict[str, str]:
        """
        Reads Key-Value pairs from a specific tab.
        """
        try:
            # Access parent spreadsheet from current worksheet
            spreadsheet = self.sheet.spreadsheet 
            ws = spreadsheet.worksheet(tab_name)
            records = ws.get_all_records() # Expects headers: Key, Value
            prompts = {r['Key']: r['Value'] for r in records if r.get('Key')}
            return prompts
        except gspread.WorksheetNotFound:
            print(f"Tab '{tab_name}' not found.")
            return {}
        except AttributeError:
             # Fallback if self.sheet is actually spreadsheet (though connect() sets it to worksheet)
             try:
                 ws = self.sheet.worksheet(tab_name)
                 records = ws.get_all_records()
                 prompts = {r['Key']: r['Value'] for r in records if r.get('Key')}
                 return prompts
             except:
                 print(f"Error accessing tab '{tab_name}' (AttributeError).")
                 return {}
        except Exception as e:
            print(f"Error reading tab '{tab_name}': {e}")
            return {}

    def get_common_rules(self, tab_name: str = "共通ルール") -> str:
        """
        Reads all values from the 'Value' column of the specified tab and joins them.
        Assumes the tab has 'Key' and 'Value' headers like other prompt tabs.
        """
        prompts = self.get_prompts_from_tab(tab_name)
        if not prompts:
            return ""
        
        # Sort by Key if possible, or just join values
        # We'll just join all values with newlines
        return "\n\n".join(prompts.values())
