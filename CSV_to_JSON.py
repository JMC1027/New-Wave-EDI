import json
import csv
from pathlib import Path


def json_to_csv(json_path, output_folder="Output/CSV_Output"):
    json_path = Path(json_path)
    output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    csv_path = output_folder / (json_path.stem + ".csv")

    # Load JSON
    with json_path.open("r", encoding="utf-8") as f:
        claims = json.load(f)

    print("Loaded JSON:", json_path.resolve())

    # ------ FIX: unwrap incorrectly structured JSON ------
    if isinstance(claims, dict):
        if "claims" in claims:
            claims = claims["claims"]
        else:
            claims = [claims]

    rows = []

    headers = [
        "ClaimID", "ClaimAmount", "PlaceOfService", "TreatmentResultingCode",
        "PayerName", "PayerID",
        "BillingProviderName", "BillingProviderNPI", "BillingProviderAddress",
        "BillingProviderCity", "BillingProviderState", "BillingProviderZip",
        "BillingProviderTaxID", "BillingProviderTaxonomy",
        "SubscriberID", "SubscriberLastName", "SubscriberFirstName",
        "SubscriberMiddle", "SubscriberDOB", "SubscriberGender",
        "SubscriberAddress", "SubscriberAddress2", "SubscriberCity",
        "SubscriberState", "SubscriberZip",
        "RenderingProviderFirstName", "RenderingProviderLastName",
        "RenderingProviderMiddle", "RenderingProviderNPI",
        "ProcedureCode", "Units", "Fee", "ToothNumber", "ProcedureDate"
    ]

    # ---- Flatten JSON ----
    for claim in claims:
        # Safety check
        if "ClaimDetails" not in claim:
            print("❌ Error: Claim missing ClaimDetails:", claim)
            continue

        for line in claim["ProcedureLines"]:
            rows.append({
                "ClaimID": claim["ClaimDetails"]["ClaimID"],
                "ClaimAmount": claim["ClaimDetails"]["ClaimAmount"],
                "PlaceOfService": claim["ClaimDetails"]["PlaceOfService"],
                "TreatmentResultingCode": claim["ClaimDetails"]["TreatmentResultingCode"],

                "PayerName": claim["Payer"]["Name"],
                "PayerID": claim["Payer"]["PayerID"],

                "BillingProviderName": claim["BillingProvider"]["ProviderName"],
                "BillingProviderNPI": claim["BillingProvider"]["NPI"],
                "BillingProviderAddress": claim["BillingProvider"]["Address"],
                "BillingProviderCity": claim["BillingProvider"]["City"],
                "BillingProviderState": claim["BillingProvider"]["State"],
                "BillingProviderZip": claim["BillingProvider"]["Zip"],
                "BillingProviderTaxID": claim["BillingProvider"]["TaxID"],
                "BillingProviderTaxonomy": claim["BillingProvider"]["Taxonomy"],

                "SubscriberID": claim["Subscriber"]["SubscriberID"],
                "SubscriberLastName": claim["Subscriber"]["LastName"],
                "SubscriberFirstName": claim["Subscriber"]["FirstName"],
                "SubscriberMiddle": claim["Subscriber"]["Middle"],
                "SubscriberDOB": claim["Subscriber"]["DOB"],
                "SubscriberGender": claim["Subscriber"]["Gender"],
                "SubscriberAddress": claim["Subscriber"]["Address"],
                "SubscriberAddress2": claim["Subscriber"]["Address2"],
                "SubscriberCity": claim["Subscriber"]["City"],
                "SubscriberState": claim["Subscriber"]["State"],
                "SubscriberZip": claim["Subscriber"]["Zip"],

                "RenderingProviderFirstName": claim["RenderingProvider"]["FirstName"],
                "RenderingProviderLastName": claim["RenderingProvider"]["LastName"],
                "RenderingProviderMiddle": claim["RenderingProvider"]["Middle"],
                "RenderingProviderNPI": claim["RenderingProvider"]["NPI"],

                "ProcedureCode": line["ProcedureCode"],
                "Units": line["Units"],
                "Fee": line["Fee"],
                "ToothNumber": line["ToothNumber"],
                "ProcedureDate": line["ProcedureDate"]
            })

    # ---- Write CSV ----
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ CSV created at: {csv_path}\n")


if __name__ == "__main__":
    json_file = "JSON_Data/mockedDentalClaim.json"
    json_to_csv(json_file)
