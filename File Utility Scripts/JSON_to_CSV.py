import os 
import csv
import json
from pathlib import Path

def json_to_csv(json_path, output_folder="Output/CSV_Output"):
    # Ensure the output folder exists
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(json_path))[0]

    # Define the path for the output CSV
    csv_path = output_folder / (base_name + ".csv")

    with open(json_path, 'r', encoding="utf-8") as f:
        data = json.load(f)

    # Open CSV file for writing
    with open(csv_path, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = [
            "ClaimID", "ClaimAmount", "PlaceOfService", "FacilityCode", "PatientSignatureOnFile", 
            "InsuranceAssignment", "ReleaseOfInformation", "TreatmentResultingCode", "ICN", 
            "PayerName", "PayerID", 
            "BillingProviderName", "BillingProviderNPI", "BillingProviderAddress", "BillingProviderAddress2", 
            "BillingProviderCity", "BillingProviderState", "BillingProviderZip", "BillingProviderTaxID", 
            "BillingProviderTaxonomy",
            "SubscriberID", "SubscriberLastName", "SubscriberFirstName", "SubscriberMiddle", "SubscriberDOB", 
            "SubscriberGender", "SubscriberAddress", "SubscriberAddress2", "SubscriberCity", "SubscriberState", 
            "SubscriberZip", 
            "RenderingProviderFirstName", "RenderingProviderLastName", "RenderingProviderMiddle", 
            "RenderingProviderNPI", 
            "ProcedureCode", "Fee", "Units", "Quantity", "ReplacementIndicator", "AreaOfOralCavity", 
            "DiagnosisCodePointer", "ToothNumber", "ToothSurfaceCode", "ToothSystem", "ProcedureDate"
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process each claim
        for claim in data:
            claim_details = claim["ClaimDetails"]
            payer = claim["Payer"]
            billing_provider = claim["BillingProvider"]
            subscriber = claim["Subscriber"]
            rendering_provider = claim["RenderingProvider"]
            procedure_lines = claim["ProcedureLines"]

            # For each procedure line, we'll write a separate row in the CSV
            for procedure in procedure_lines:
                row = {
                    "ClaimID": claim_details.get("ClaimID", ""),
                    "ClaimAmount": claim_details.get("ClaimAmount", ""),
                    "PlaceOfService": claim_details.get("PlaceOfService", ""),
                    "FacilityCode": claim_details.get("FacilityCode", ""),
                    "PatientSignatureOnFile": claim_details.get("PatientSignatureOnFile", ""),
                    "InsuranceAssignment": claim_details.get("InsuranceAssignment", ""),
                    "ReleaseOfInformation": claim_details.get("ReleaseOfInformation", ""),
                    "TreatmentResultingCode": claim_details.get("TreatmentResultingCode", ""),
                    "ICN": claim_details.get("ICN", ""),
                    "PayerName": payer.get("Name", ""),
                    "PayerID": payer.get("PayerID", ""),
                    "BillingProviderName": billing_provider.get("ProviderName", ""),
                    "BillingProviderNPI": billing_provider.get("NPI", ""),
                    "BillingProviderAddress": billing_provider.get("Address", ""),
                    "BillingProviderAddress2": billing_provider.get("Address2", ""),
                    "BillingProviderCity": billing_provider.get("City", ""),
                    "BillingProviderState": billing_provider.get("State", ""),
                    "BillingProviderZip": billing_provider.get("Zip", ""),
                    "BillingProviderTaxID": billing_provider.get("TaxID", ""),
                    "BillingProviderTaxonomy": billing_provider.get("Taxonomy", ""),
                    "SubscriberID": subscriber.get("SubscriberID", ""),
                    "SubscriberLastName": subscriber.get("LastName", ""),
                    "SubscriberFirstName": subscriber.get("FirstName", ""),
                    "SubscriberMiddle": subscriber.get("Middle", ""),
                    "SubscriberDOB": subscriber.get("DOB", ""),
                    "SubscriberGender": subscriber.get("Gender", ""),
                    "SubscriberAddress": subscriber.get("Address", ""),
                    "SubscriberAddress2": subscriber.get("Address2", ""),
                    "SubscriberCity": subscriber.get("City", ""),
                    "SubscriberState": subscriber.get("State", ""),
                    "SubscriberZip": subscriber.get("Zip", ""),
                    "RenderingProviderFirstName": rendering_provider.get("FirstName", ""),
                    "RenderingProviderLastName": rendering_provider.get("LastName", ""),
                    "RenderingProviderMiddle": rendering_provider.get("Middle", ""),
                    "RenderingProviderNPI": rendering_provider.get("NPI", ""),
                    "ProcedureCode": procedure.get("ProcedureCode", ""),
                    "Fee": procedure.get("Fee", ""),
                    "Units": procedure.get("Units", ""),
                    "Quantity": procedure.get("Quantity", ""),
                    "ReplacementIndicator": procedure.get("ReplacementIndicator", ""),
                    "AreaOfOralCavity": procedure.get("AreaOfOralCavity", ""),
                    "DiagnosisCodePointer": procedure.get("DiagnosisCodePointer", ""),
                    "ToothNumber": procedure.get("ToothNumber", ""),
                    "ToothSurfaceCode": procedure.get("ToothSurfaceCode", ""),
                    "ToothSystem": procedure.get("ToothSystem", ""),
                    "ProcedureDate": procedure.get("ProcedureDate", "")
                }

                # Write row to CSV
                writer.writerow(row)

    print(f"CSV file created at: {csv_path}")

# Example usage
json_file = "Output/JSON_Output/mockedDentalClaim.json"
json_to_csv(json_file)
