import os
import json
from datetime import datetime
from pyx12.x12file import X12Reader
from pyx12.errors import X12Error
from io import StringIO
from pathlib import Path

# -------------------------------
# Utility functions
# -------------------------------

def format_x12_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y%m%d")
    except ValueError:
        return ""

def get_datetime():
    now = datetime.now()
    return now.strftime("%y%m%d"), now.strftime("%H%M")

def full_date():
    return datetime.now().strftime("%Y%m%d")

def get_field(data, *keys, default=""): # Safely get nested fields from a dict
    d = data
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d

# -------------------------------
# Generate Dental X12
# -------------------------------

def generate_dental_x12(json_file_path):
    # Load JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    date, time = get_datetime()
    full_formatted_date = full_date()
    claim = json_data[0]

    # ISA / GS control numbers
    control_number = "000000001"  # 9 characters

    # -------------------------------
    # Build X12 segments
    # -------------------------------

    sender_id = "SENDERID".ljust(15)
    receiver_id = "RECEIVERID".ljust(15)
    auth_info = ''.ljust(10)
    security_info = ''.ljust(10)

    x12_output = []
    x12_output.append(f"ISA*00*{auth_info}*00*{security_info}*ZZ*{sender_id}*ZZ*{receiver_id}*{date}*{time}*^*00501*{control_number}*1*T*:~")
    x12_output.append(f"GS*HC*SENDERID*RECEIVERID*{full_formatted_date}*{time}*{control_number}*X*005010X224A2~")
    x12_output.append("ST*837*0001*005010X224A2~")
    x12_output.append(f"BHT*0019*00*{get_field(claim, 'ClaimDetails', 'ClaimID')}*{full_formatted_date}*{time}*CH~")
    x12_output.append("NM1*41*2*Organization Name*****46*WTPID000007~")
    x12_output.append("PER*IC*Help Desk*TE*18005551234~")
    x12_output.append(f"NM1*40*2*{get_field(claim, 'Payer', 'Name')}*****46*{get_field(claim, 'Payer', 'PayerID')}~")
    x12_output.append("HL*1**20*1~")
    x12_output.append(f"NM1*85*2*{get_field(claim, 'BillingProvider', 'ProviderName')}*****XX*{get_field(claim, 'BillingProvider', 'NPI')}~")
    
    bp_addr2 = get_field(claim, 'BillingProvider', 'Address2')
    if bp_addr2:
        x12_output.append(f"N3*{get_field(claim, 'BillingProvider', 'Address')}*{bp_addr2}~")
    else:
        x12_output.append(f"N3*{get_field(claim, 'BillingProvider', 'Address')}~")
    
    x12_output.append(f"N4*{get_field(claim, 'BillingProvider', 'City')}*{get_field(claim, 'BillingProvider', 'State')}*{get_field(claim, 'BillingProvider', 'Zip')}~")
    x12_output.append(f"REF*EI*{get_field(claim, 'BillingProvider', 'TaxID')}~")
    
    x12_output.append("HL*2*1*22*0~")
    x12_output.append("SBR*S*18******MA~")  # MA = Commercial Dental
    x12_output.append(f"NM1*IL*1*{get_field(claim, 'Subscriber', 'LastName')}*{get_field(claim, 'Subscriber', 'FirstName')}*{get_field(claim, 'Subscriber', 'Middle')}**MI*{get_field(claim, 'Subscriber', 'SubscriberID')}~")
    
    sub_addr2 = get_field(claim, 'Subscriber', 'Address2')
    if sub_addr2:
        x12_output.append(f"N3*{get_field(claim, 'Subscriber', 'Address')}*{sub_addr2}~")
    else:
        x12_output.append(f"N3*{get_field(claim, 'Subscriber', 'Address')}~")
    
    x12_output.append(f"N4*{get_field(claim, 'Subscriber', 'City')}*{get_field(claim, 'Subscriber', 'State')}*{get_field(claim, 'Subscriber', 'Zip')}~")
    x12_output.append(f"DMG*D8*{format_x12_date(get_field(claim, 'Subscriber', 'DOB'))}*{get_field(claim, 'Subscriber', 'Gender')}~")
    x12_output.append(f"NM1*PR*2*{get_field(claim, 'Payer', 'Name')}*****PI*{get_field(claim, 'Payer', 'PayerID')}~")
   
    facility_code = get_field(claim, 'ClaimDetails', 'FacilityCode') or 'B'
    treatment_code = get_field(claim, 'ClaimDetails', 'TreatmentResultingCode') or 'B'
    x12_output.append(f"CLM*{get_field(claim, 'ClaimDetails', 'ClaimID')}*{get_field(claim, 'ClaimDetails', 'ClaimAmount')}***{get_field(claim, 'ClaimDetails', 'PlaceOfService')}:{facility_code}:1*Y*A*Y*Y*{treatment_code}~")

    
    x12_output.append(f"NM1*82*1*{get_field(claim, 'RenderingProvider', 'LastName')}*{get_field(claim, 'RenderingProvider', 'FirstName')}*{get_field(claim, 'RenderingProvider', 'Middle')}**XX*{get_field(claim, 'RenderingProvider', 'NPI')}~")
    x12_output.append(f"PRV*PE*PXC*{get_field(claim, 'BillingProvider', 'Taxonomy')}~")

    # Procedure lines
    lx_counter = 1
    for line in get_field(claim, 'ProcedureLines', default=[]):
        procedure_code = get_field(line, 'ProcedureCode')
        if not procedure_code.strip():
            continue
        fee = get_field(line, 'Fee')
        quantity = get_field(line, 'Quantity')
        replacement_indicator = get_field(line, 'ReplacementIndicator')
        aooc = get_field(line, 'AreaOfOralCavity')
        area_of_oral_cavity = ":".join(aooc[:5]) if aooc else ""
        diag_ptr = get_field(line, 'DiagnosisCodePointer')
        diagnosis_pointer = ":".join(diag_ptr[:5]) if diag_ptr else ""

        x12_output.append(f"LX*{lx_counter}~")
        sv3_fields = [
            f"AD:{procedure_code}",
            str(fee) if fee else "",
            "",  # unused
            area_of_oral_cavity,
            replacement_indicator,
            quantity,
            diagnosis_pointer,
        ]
        x12_output.append("SV3*" + "*".join(sv3_fields) + "~")
        x12_output.append(f"DTP*472*D8*{full_formatted_date}~")
        tooth_number = get_field(line, 'ToothNumber', default='')
        tooth_surface = get_field(line, 'ToothSurfaceCode', default='')

        # Only output TOO segment if there’s real data
        tooth_surface_fmt = ":".join(tooth_surface[:5]) if tooth_surface.strip() else ""
        if tooth_number.strip() or tooth_surface_fmt:
            x12_output.append(f"TOO*JP*{tooth_number}*{tooth_surface_fmt}~")

        lx_counter += 1

    # SE / GE / IEA segments
    st_index = next(i for i, seg in enumerate(x12_output) if seg.startswith("ST*"))
    segment_count = len(x12_output) - st_index + 1
    x12_output.append(f"SE*{segment_count}*0001~")
    x12_output.append(f"GE*1*{control_number}~")
    x12_output.append(f"IEA*1*{control_number}~")

    # Write files
    x12_dir = Path("Output/.837D")
    x12_dir.mkdir(parents=True, exist_ok=True)
    error_dir = Path("Output/X12_Error")
    error_dir.mkdir(parents=True, exist_ok=True)

    x12_path = x12_dir / "dental_claim_837.txt"
    #edi_string = '\n'.join(x12_output)
    edi_string = "".join(x12_output)

    with open(x12_path, "w", encoding="utf-8") as f:
        f.write(edi_string)
    print(f"X12 file written to: {x12_path}")

    # Validate with X12Reader
    edi_file_obj = StringIO(edi_string)
    errors = []
    try:
        x12_reader = X12Reader(edi_file_obj)
        for seg in x12_reader:
            if hasattr(seg, 'errors') and seg.errors:
                for err in seg.errors:
                    errors.append(str(err))
    except X12Error as e:
        errors.append(str(e))

    error_file = error_dir / ".837D_Errors.txt"
    with open(error_file, "w", encoding="utf-8") as f:
        if errors:
            for err in errors:
                f.write(err + "\n")
            print(f"Errors written to: {error_file}")
        else:
            f.write("No X12 errors detected.\n")
            print(f"No X12 errors detected. File created: {error_file}")

# -------------------------------
# Run
# -------------------------------

json_file_path = "JSON_Data/mockedDentalClaim.json"
# generate_dental_x12(json_file_path)
