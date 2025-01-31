from typing import List, Any
from gspread import (
    Spreadsheet,
    Worksheet
)
import gspread

from core.config import settings

# Authentication by GOOGLE API KEY
gc = gspread.api_key(settings.GOOGLE_API_KEY)

class GSheets:
    def __init__(self, spreadsheet_url: str, worksheet_name: str | None = None):
        self.spreadsheet_url = spreadsheet_url
        self.worksheet_name = worksheet_name
    
    @property
    def spreadsheet(self) -> Spreadsheet:
        """Opens a spreadsheet specified by `url`."""
        return gc.open_by_url(url=self.spreadsheet_url)
    
    @property
    def worksheet(self) -> Worksheet:
        """Returns a worksheet with specified `url`."""
        if not self.worksheet_name:
            return self.spreadsheet.get_worksheet(0)
        else:
            return self.spreadsheet.worksheet(self.worksheet_name)

    @property
    def worksheets(self) -> List[Worksheet]:
        """Returns a list of all `worksheets` in a spreadsheet."""
        return self.spreadsheet.worksheets()
    
    @staticmethod
    def create_spreadsheet(name: str, folder_id: str | None = None) -> Spreadsheet:
        """Create a new spreadsheet."""
        return gc.create(title=name, folder_id=folder_id)