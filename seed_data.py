import os
import random
from dotenv import load_dotenv
import stripe

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

names = ["Acme Corp", "Blue Fin LLC", "Carter Design", "Dunlop Repair"]

for i in range(12):
    amount = random.randrange(1500, 40000, 100)
    stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        payment_method="pm_card_visa",
        confirm=True,
        description=f"Invoice #{1000 + i} - {random.choice(names)}",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
    )
    print(f"Created payment {i + 1}: ${amount / 100:.2f}")

print("Done.")