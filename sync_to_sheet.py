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


def existing_payment_ids(worksheet):
    """Payment IDs already in column A, excluding the header."""
    column = worksheet.col_values(1)
    if not column:
        return set()
    return set(column[1:])


def ensure_headers(worksheet):
    if not worksheet.col_values(1):
        worksheet.update(values=[HEADERS], range_name="A1")
        print("Wrote headers to empty sheet")


def main():
    payments = fetch_all_payments()

    worksheet = get_worksheet()
    ensure_headers(worksheet)

    already_there = existing_payment_ids(worksheet)
    new_payments = [p for p in payments if p.id not in already_there]

    skipped = len(payments) - len(new_payments)

    if not new_payments:
        print(f"\nNothing new. {skipped} payments already in the sheet.")
        return

    # Oldest first, so the sheet reads chronologically as it grows.
    rows = [to_row(p) for p in reversed(new_payments)]
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")

    print(f"\nAdded {len(rows)} new rows. Skipped {skipped} already present.")


if __name__ == "__main__":
    main()