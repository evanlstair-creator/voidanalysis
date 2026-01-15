import os
import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


PLACES_HEADERS = [
    "place_id",
    "name",
    "address",
    "latitude",
    "longitude",
    "types",
    "rating",
    "user_ratings_total",
    "business_status",
    "first_seen",
    "last_seen",
    "times_seen",
    "matched_chain",
    "match_score",
]

SEARCHES_HEADERS = [
    "search_id",
    "latitude",
    "longitude",
    "radius_miles",
    "search_date",
    "total_places",
    "matched_chains",
    "missing_retailers",
    "coverage_pct",
    "api_calls_used",
]


class GoogleSheetsDB:
    def __init__(self, spreadsheet_id, credentials_path=None):
        if not credentials_path:
            credentials_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
        credentials_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
        if not credentials_path and not credentials_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS is not set")

        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path

        if credentials_json:
            info = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
        else:
            creds = Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(spreadsheet_id)

        self.places_ws = self._ensure_worksheet("Places", PLACES_HEADERS)
        self.searches_ws = self._ensure_worksheet("Searches", SEARCHES_HEADERS)

        self.place_ids = self._load_place_ids()
        self.next_search_id = self._get_next_search_id()

    def _ensure_worksheet(self, title, headers):
        try:
            worksheet = self.sheet.worksheet(title)
        except gspread.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(title=title, rows=1000, cols=len(headers))

        existing_headers = worksheet.row_values(1)
        if existing_headers != headers:
            worksheet.update("A1", [headers])
        return worksheet

    def _load_place_ids(self):
        values = self.places_ws.col_values(1)
        return set(values[1:])

    def _get_next_search_id(self):
        values = self.searches_ws.col_values(1)
        max_id = 0
        for value in values[1:]:
            try:
                max_id = max(max_id, int(value))
            except ValueError:
                continue
        return max_id + 1

    def _format_types(self, types_value):
        if isinstance(types_value, list):
            return ", ".join(types_value)
        return types_value or ""

    def save_places(self, places):
        if not places:
            return 0

        now = datetime.utcnow().isoformat()
        rows = []

        for place in places:
            place_id = place.get("place_id")
            if not place_id or place_id in self.place_ids:
                continue

            self.place_ids.add(place_id)
            rows.append([
                place_id,
                place.get("name", ""),
                place.get("address", ""),
                place.get("latitude"),
                place.get("longitude"),
                self._format_types(place.get("types")),
                place.get("rating"),
                place.get("user_ratings_total"),
                place.get("business_status"),
                now,
                now,
                1,
                place.get("matched_retailer") or "",
                place.get("match_score") or 0,
            ])

        if rows:
            self.places_ws.append_rows(rows, value_input_option="USER_ENTERED")

        return len(rows)

    def save_search(self, search_data):
        search_id = self.next_search_id
        self.next_search_id += 1

        row = [
            search_id,
            search_data.get("latitude"),
            search_data.get("longitude"),
            search_data.get("radius_miles"),
            datetime.utcnow().isoformat(),
            search_data.get("total_places"),
            search_data.get("matched_chains"),
            search_data.get("missing_retailers"),
            search_data.get("coverage_pct"),
            search_data.get("api_calls_used"),
        ]

        self.searches_ws.append_row(row, value_input_option="USER_ENTERED")
        return search_id
