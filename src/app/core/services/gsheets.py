from typing import List
from gspread import (
    Spreadsheet,
    Worksheet
)

import gspread

from core.config import settings
from core import exc  

# Authentication by GOOGLE API KEY
gc = gspread.api_key(settings.GOOGLE_API_KEY)

class GSheets:
    def __init__(self, spreadsheet_url: str, worksheet_name: str | None = None):
        self.spreadsheet_url = spreadsheet_url
        self.worksheet_name = worksheet_name
    
    @property
    def spreadsheet(self) -> Spreadsheet:
        """Opens a spreadsheet specified by `url`."""
        try:
            return gc.open_by_url(url=self.spreadsheet_url)
        except:
            raise exc.INTERNAL_SERVER_ERROR(
                detail="An error occurred while processing work with Google Sheets."
            )

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
    def create_spreadsheet(name: str, folder_name: str | None = None) -> Spreadsheet:
        """Create a new spreadsheet."""
        return gc.create(title=name, folder_id=folder_name)
    
    def find_by(self, *, query: str):
        cell = self.worksheet.find(query=query)
        if not cell:
            raise exc.NOT_FOUND(
                detail="The cell of spreadsheet not found.")
        return cell
    
    def get_all(self) -> List[List[str | int | float]]:
        result = self.worksheet.get_all_values()
        if not result:
            raise exc.NOT_FOUND(
                detail="None found all")
        return result
    
    def get_row(self, row: int):
        result = self.worksheet.row_values(row=row)
        if not result:
            raise exc.NOT_FOUND(
                detail="None found row")
        return result