import csv
import json
from pathlib import Path
from collections import defaultdict

def csv_to_nested_json(csv_path, output_folder="Output/JSON_Output"):
    csv_path = Path(csv_path)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Create JSON output file path
    json_path = output_folder / (csv_path.stem + ".json")

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Group rows by ClaimID to build nested structure
    claims_dict = defaultdict(lambda: {
        "ClaimDetails": {},
        "Payer": {},
        "BillingProvider": {},
        "Subscriber": {},
        "RenderingProvider": {},
        "ProcedureLines": []
    })

    # Iterate through the rows and build nested JSON
    for row in rows:
        claim_id = row.get("ClaimID", "")
        claim = claims_dict[claim_id]

        # ClaimDetails
        claim["ClaimDetails"].update({
            "ClaimID": row.get("ClaimID", ""),
            "ClaimAmount": row.get("ClaimAmount", ""),
            "PlaceOfService": row.get("PlaceOfService", ""),
            "FacilityCode": row.get("FacilityCode", ""),
            "PatientSignatureOnFile": row.get("PatientSignatureOnFile", ""),
            "InsuranceAssignment": row.get("InsuranceAssignment", ""),
            "ReleaseOfInformation": row.get("ReleaseOfInformation", ""),
            "TreatmentResultingCode": row.get("TreatmentResultingCode", ""),
            "ICN": row.get("ICN", "")
        })

        # Payer
        claim["Payer"].update({
            "Name": row.get("PayerName", ""),
            "PayerID": row.get("PayerID", "")
        })

        # Billing Provider
        claim["BillingProvider"].update({
            "ProviderName": row.get("BillingProviderName", ""),
            "NPI": row.get("BillingProviderNPI", ""),
            "Address": row.get("BillingProviderAddress", ""),
            "Address2": row.get("BillingProviderAddress2", ""),
            "City": row.get("BillingProviderCity", ""),
            "State": row.get("BillingProviderState", ""),
            "Zip": row.get("BillingProviderZip", ""),
            "TaxID": row.get("BillingProviderTaxID", ""),
            "Taxonomy": row.get("BillingProviderTaxonomy", "")
        })

        # Subscriber
        claim["Subscriber"].update({
            "SubscriberID": row.get("SubscriberID", ""),
            "LastName": row.get("SubscriberLastName", ""),
            "FirstName": row.get("SubscriberFirstName", ""),
            "Middle": row.get("SubscriberMiddle", ""),
            "DOB": row.get("SubscriberDOB", ""),
            "Gender": row.get("SubscriberGender", ""),
            "Address": row.get("SubscriberAddress", ""),
            "Address2": row.get("SubscriberAddress2", ""),
            "City": row.get("SubscriberCity", ""),
            "State": row.get("SubscriberState", ""),
            "Zip": row.get("SubscriberZip", "")
        })

        # Rendering Provider
        claim["RenderingProvider"].update({
            "FirstName": row.get("RenderingProviderFirstName", ""),
            "LastName": row.get("RenderingProviderLastName", ""),
            "Middle": row.get("RenderingProviderMiddle", ""),
            "NPI": row.get("RenderingProviderNPI", "")
        })

        # ProcedureLines (append each row as a line)
        procedure_line = {
            "ProcedureCode": row.get("ProcedureCode", ""),
            "Fee": row.get("Fee", ""),
            "Units": row.get("Units", ""),
            "Quantity": row.get("Quantity", ""),
            "ReplacementIndicator": row.get("ReplacementIndicator", ""),
            "AreaOfOralCavity": row.get("AreaOfOralCavity", ""),
            "DiagnosisCodePointer": row.get("DiagnosisCodePointer", ""),
            "ToothNumber": row.get("ToothNumber", ""),
            "ToothSurfaceCode": row.get("ToothSurfaceCode", ""),
            "ToothSystem": row.get("ToothSystem", ""),
            "ProcedureDate": row.get("ProcedureDate", "")
        }
        claim["ProcedureLines"].append(procedure_line)

    # Convert dict to list
    claims_list = list(claims_dict.values())

    # Write JSON output
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(claims_list, f, indent=4)

    print(f"Nested JSON created at: {json_path}")

# Example usage
csv_file = "Output/CSV_Output/mockedDentalClaim.csv"
csv_to_nested_json(csv_file)
