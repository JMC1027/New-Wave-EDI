import json
import csv
from pathlib import Path

def json_to_csv(json_path, output_folder="Output/CSV_Output"):
    json_path = Path(json_path)
    output_folder = Path(output_folder)

    # Create output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # Output CSV file path
    csv_path = output_folder / (json_path.stem + ".csv")

    # Read JSON data
    with json_path.open(mode='r', encoding='utf-8') as f:
        data = json.load(f)

    # Prepare CSV rows
    csv_rows = []

    # CSV headers
    headers = [
        "ClaimID","PatientID","PatientFirstName","PatientLastName","PatientDOB","PatientGender",
        "PatientAddress","PatientCity","PatientState","PatientZip",
        "SubscriberID","InsurancePayerName","InsurancePayerID",
        "ProviderNPI","ProviderFirstName","ProviderLastName","ProviderTaxonomy",
        "ServiceDate","PlaceOfService",
        "ToothNumber","Surface","ProcedureCode","ProcedureDescription",
        "Units","Fee","DiagnosisCode","ProcedureModifier"
    ]

    # Flatten JSON
    for claim in data:
        for line in claim.get("ProcedureLines", []):
            row = {header: "" for header in headers}  # initialize empty row
            row.update({
                "ClaimID": claim.get("ClaimID", ""),
                "PatientID": claim.get("PatientID", ""),
                "PatientFirstName": claim.get("PatientFirstName", ""),
                "PatientLastName": claim.get("PatientLastName", ""),
                "PatientDOB": claim.get("PatientDOB", ""),
                "PatientGender": claim.get("PatientGender", ""),
                "PatientAddress": claim.get("PatientAddress", ""),
                "PatientCity": claim.get("PatientCity", ""),
                "PatientState": claim.get("PatientState", ""),
                "PatientZip": claim.get("PatientZip", ""),
                "SubscriberID": claim.get("SubscriberID", ""),
                "InsurancePayerName": claim.get("InsurancePayerName", ""),
                "InsurancePayerID": claim.get("InsurancePayerID", ""),
                "ProviderNPI": claim.get("ProviderNPI", ""),
                "ProviderFirstName": claim.get("ProviderFirstName", ""),
                "ProviderLastName": claim.get("ProviderLastName", ""),
                "ProviderTaxonomy": claim.get("ProviderTaxonomy", ""),
                "ServiceDate": claim.get("ServiceDate", ""),
                "PlaceOfService": claim.get("PlaceOfService", ""),
                "ToothNumber": line.get("ToothNumber", ""),
                "Surface": line.get("Surface", ""),
                "ProcedureCode": line.get("ProcedureCode", ""),
                "ProcedureDescription": line.get("ProcedureDescription", ""),
                "Units": line.get("Units", ""),
                "Fee": line.get("Fee", ""),
                "DiagnosisCode": line.get("DiagnosisCode", ""),
                "ProcedureModifier": line.get("ProcedureModifier", "")
            })
            csv_rows.append(row)

    # Write CSV
    with csv_path.open(mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"CSV created at: {csv_path}")


# -------------------------
# Run script with your file
# -------------------------
json_file = "Output/JSON_Output/mockedDentalClaim.json"
json_to_csv(json_file)
