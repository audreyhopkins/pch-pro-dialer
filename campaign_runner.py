import csv
import time
from vapi import Vapi
import os

vapi = Vapi(token=os.getenv("VAPI_API_KEY"))

def start_campaign(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            customer = {
                "number": row["number"],
                "name": row["full_name"],
                "metadata": {
                    "address": row["address"],
                    "zip": row["zip"],
                    "state": row["state"],
                    "age": row["age"],
                    "citizenship": row["citizenship"],
                    "prize_amount": row["prize_amount"]
                }
            }

            vapi.calls.create(
                assistant_id=os.getenv("ASSISTANT_ID"),
                phone_number_id=os.getenv("PHONE_NUMBER_ID"),
                customer=customer,
                metadata={"campaign": "Prize_Claim"}
            )

            print(f"Started call for {customer['name']} at {customer['number']}")
            time.sleep(2)
