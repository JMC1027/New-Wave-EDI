import json
from datetime import datetime
from pathlib import Path

def format_x12_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")
    except:
        return ""

def get_field(data, *keys, default=""):
    d = data
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d

def generate_dental_x12_single(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        claims = json.load(f)

    now = datetime.now()
    date = now.strftime("%y%m%d")
    time = now.strftime("%H%M")
    full_date = now.strftime("%Y%m%d")
    control_number = 1  # increment per claim

    output_dir = Path("Output/.837D")
    output_dir.mkdir(parents=True, exist_ok=True)

    for claim in claims:
        x12_output = []

        ctrl_num_str = str(control_number).zfill(9)
        st_number = "0001"

        # ISA / GS / ST
        x12_output.append(f"ISA*00*{'':10}*00*{'':10}*ZZ*SENDERID       *ZZ*RECEIVERID     *{date}*{time}*^*00501*{ctrl_num_str}*1*T*:~")
        x12_output.append(f"GS*HC*SENDERID*RECEIVERID*{full_date}*{time}*{control_number}*X*005010X224A2~")
        x12_output.append(f"ST*837*{st_number}*005010X224A2~")
        st_start_index = len(x12_output)

        # BHT
        x12_output.append(f"BHT*0019*00*{get_field(claim, 'ClaimDetails', 'ClaimID')}*{full_date}*{time}*CH~")
        x12_output.append("NM1*41*2*Organization Name*****46*WTPID000007~")
        x12_output.append("PER*IC*Help Desk*TE*18005551234~")
        x12_output.append(f"NM1*40*2*{get_field(claim, 'Payer', 'Name')}*****46*{get_field(claim, 'Payer', 'PayerID')}~")

        # Billing Provider
        x12_output.append("HL*1**20*1~")
        x12_output.append(f"NM1*85*2*{get_field(claim, 'BillingProvider', 'ProviderName')}*****XX*{get_field(claim, 'BillingProvider', 'NPI')}~")
        addr2 = get_field(claim, 'BillingProvider', 'Address2')
        if addr2:
            x12_output.append(f"N3*{get_field(claim, 'BillingProvider', 'Address')}*{addr2}~")
        else:
            x12_output.append(f"N3*{get_field(claim, 'BillingProvider', 'Address')}~")
        x12_output.append(f"N4*{get_field(claim, 'BillingProvider', 'City')}*{get_field(claim, 'BillingProvider', 'State')}*{get_field(claim, 'BillingProvider', 'Zip')}~")
        x12_output.append(f"REF*EI*{get_field(claim, 'BillingProvider', 'TaxID')}~")

        # Subscriber
        x12_output.append("HL*2*1*22*0~")
        x12_output.append("SBR*S*18******MA~")
        x12_output.append(f"NM1*IL*1*{get_field(claim, 'Subscriber', 'LastName')}*{get_field(claim, 'Subscriber', 'FirstName')}*{get_field(claim, 'Subscriber', 'Middle')}**MI*{get_field(claim, 'Subscriber', 'SubscriberID')}~")
        addr2 = get_field(claim, 'Subscriber', 'Address2')
        if addr2:
            x12_output.append(f"N3*{get_field(claim, 'Subscriber', 'Address')}*{addr2}~")
        else:
            x12_output.append(f"N3*{get_field(claim, 'Subscriber', 'Address')}~")
        x12_output.append(f"N4*{get_field(claim, 'Subscriber', 'City')}*{get_field(claim, 'Subscriber', 'State')}*{get_field(claim, 'Subscriber', 'Zip')}~")
        x12_output.append(f"DMG*D8*{format_x12_date(get_field(claim, 'Subscriber', 'DOB'))}*{get_field(claim, 'Subscriber', 'Gender')}~")
        x12_output.append(f"NM1*PR*2*{get_field(claim, 'Payer', 'Name')}*****PI*{get_field(claim, 'Payer', 'PayerID')}~")

        # Claim info
        facility_code = get_field(claim, 'ClaimDetails', 'FacilityCode') or 'B'
        treatment_code = get_field(claim, 'ClaimDetails', 'TreatmentResultingCode') or 'B'
        x12_output.append(f"CLM*{get_field(claim, 'ClaimDetails', 'ClaimID')}*{get_field(claim, 'ClaimDetails', 'ClaimAmount')}***{get_field(claim, 'ClaimDetails', 'PlaceOfService')}:{facility_code}:1*Y*A*Y*Y*{treatment_code}~")

        # Rendering provider
        x12_output.append(f"NM1*82*1*{get_field(claim, 'RenderingProvider', 'LastName')}*{get_field(claim, 'RenderingProvider', 'FirstName')}*{get_field(claim, 'RenderingProvider', 'Middle')}**XX*{get_field(claim, 'RenderingProvider', 'NPI')}~")
        x12_output.append(f"PRV*PE*PXC*{get_field(claim, 'BillingProvider', 'Taxonomy')}~")

        # Procedure lines
        lx_counter = 1
        for line in get_field(claim, 'ProcedureLines', default=[]):
            x12_output.append(f"LX*{lx_counter}~")
            x12_output.append(f"SV3*AD:{get_field(line,'ProcedureCode')}*{get_field(line,'Fee')}**{get_field(line,'AreaOfOralCavity')}*{get_field(line,'ReplacementIndicator')}*{get_field(line,'Quantity')}*~")
            x12_output.append(f"DTP*472*D8*{format_x12_date(get_field(line, 'ProcedureDate'))}~")
            tooth_num = get_field(line, 'ToothNumber')
            tooth_surf = get_field(line, 'ToothSurfaceCode')
            tooth_system = get_field(line, 'ToothSystem', default='JP')
            if tooth_num or tooth_surf:
                x12_output.append(f"TOO*{tooth_system}*{tooth_num}*{tooth_surf}~")
            lx_counter += 1

        # SE
        segment_count = len(x12_output) - st_start_index + 1
        x12_output.append(f"SE*{segment_count}*{st_number}~")

        # GE / IEA
        x12_output.append(f"GE*1*{control_number}~")
        x12_output.append(f"IEA*1*{ctrl_num_str}~")

        # Write file per claim
        claim_id = get_field(claim, 'ClaimDetails', 'ClaimID')
        file_path = output_dir / f"Single_.837D.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(x12_output))

        print(f"X12 file for claim {claim_id} written: {file_path}")
        control_number += 1
