from typing import List
import gspread

from core.config import settings
from core import exc

gc = gspread.service_account(
    filename=settings.CREDS_DIR,
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"] 
)

class GSheets:
    def __init__(self, spreadsheet_url: str, worksheet_name: str | None = None):
        self.spreadsheet_url = spreadsheet_url
        self.worksheet_name = worksheet_name
    
    @property
    def spreadsheet(self) -> gspread.Spreadsheet:
        """Opens a spreadsheet specified by `url`."""
        try:
            return gc.open_by_url(url=self.spreadsheet_url)
        except:
            raise exc.INTERNAL_SERVER_ERROR(
                detail="An error occurred while processing work with Google Sheets."
            )

    @property
    def worksheet(self) -> gspread.Worksheet:
        """Returns a worksheet with specified `url`."""
        if not self.worksheet_name:
            return self.spreadsheet.get_worksheet(0)
        else:
            return self.spreadsheet.worksheet(self.worksheet_name)

    @property
    def worksheets(self) -> List[gspread.Worksheet]:
        """Returns a list of all `worksheets` in a spreadsheet."""
        return self.spreadsheet.worksheets()

    @staticmethod
    def create_spreadsheet(name: str) -> gspread.Spreadsheet:
        """Create a new spreadsheet."""
        gc.create(title=name)
    
    def find_by(self, *, query: str):
        cell = self.worksheet.find(query=query)
        if not cell:
            raise exc.NOT_FOUND(
                detail="The cell of spreadsheet not found.")
        return cell