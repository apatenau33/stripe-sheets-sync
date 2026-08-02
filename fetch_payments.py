import os
from datetime import datetime, timezone

from dotenv import load_dotenv
import stripe

from helpers import log, setup_logging

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

PAGE_SIZE = 10


def fetch_all_payments():
    payments = []
    starting_after = None
    page = 0

    while True:
        page += 1
        params = {"limit": PAGE_SIZE}
        if starting_after:
            params["starting_after"] = starting_after

        response = stripe.PaymentIntent.list(**params)
        batch = response.data
        payments.extend(batch)
        log.info(f"Page {page}: got {len(batch)} (running total: {len(payments)})")

        if not response.has_more:
            break

        starting_after = batch[-1].id

    return payments


def main():
    setup_logging()
    payments = fetch_all_payments()
    log.info(f"Total: {len(payments)} payments")

    for p in payments:
        created = datetime.fromtimestamp(p.created, tz=timezone.utc)
        amount = p.amount / 100
        log.info(
            f"{created:%Y-%m-%d %H:%M}  ${amount:>8,.2f}  "
            f"{p.status:<10} {p.description or ''}"
        )


if __name__ == "__main__":
    main()