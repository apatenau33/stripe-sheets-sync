import os
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

from fetch_payments import fetch_all_payments

SHEET_NAME = "Stripe Payments"
CREDENTIALS_FILE = "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["Payment ID", "Date", "Amount", "Status", "Description"]


def get_worksheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def to_row(payment):
    created = datetime.fromtimestamp(payment.created, tz=timezone.utc)
    return [
        payment.id,
        created.strftime("%Y-%m-%d %H:%M"),
        payment.amount / 100,
        payment.status,
        payment.description or "",
    ]


def main():
    payments = fetch_all_payments()
    rows = [to_row(p) for p in payments]

    worksheet = get_worksheet()
    worksheet.clear()
    worksheet.update(values=[HEADERS] + rows, range_name="A1")

    print(f"\nWrote {len(rows)} rows to '{SHEET_NAME}'")


if __name__ == "__main__":
    main()