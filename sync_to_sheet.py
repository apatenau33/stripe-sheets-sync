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


from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

from fetch_payments import fetch_all_payments
from helpers import log, setup_logging, with_retries

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
    column = worksheet.col_values(1)
    if not column:
        return set()
    return set(column[1:])


def ensure_headers(worksheet):
    if not worksheet.col_values(1):
        worksheet.update(values=[HEADERS], range_name="A1")
        log.info("Wrote headers to empty sheet")


def main():
    setup_logging()
    log.info("Sync started")

    try:
        payments = with_retries(fetch_all_payments, description="Stripe fetch")
        log.info(f"Fetched {len(payments)} payments from Stripe")

        worksheet = with_retries(get_worksheet, description="Sheets connect")
        ensure_headers(worksheet)

        already_there = existing_payment_ids(worksheet)
        new_payments = [p for p in payments if p.id not in already_there]
        skipped = len(payments) - len(new_payments)

        if not new_payments:
            log.info(f"Nothing new - {skipped} payments already present")
            return

        rows = [to_row(p) for p in reversed(new_payments)]
        with_retries(
            lambda: worksheet.append_rows(rows, value_input_option="USER_ENTERED"),
            description="Sheets write",
        )
        log.info(f"Added {len(rows)} new rows, skipped {skipped} already present")

    except Exception:
        log.exception("Sync failed")
        raise

    log.info("Sync finished")


if __name__ == "__main__":
    main()