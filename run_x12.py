import json
import csv
import traceback
from generateDentalX12 import generate_dental_x12

def generate():
    try:
        json_file_path = "Output/JSON_Output/mockedDentalClaim.json"
        generate_dental_x12(json_file_path)
    except Exception as e:
        print(f"Failed to generate X12 file: {e}")
        traceback.print_exc()

generate()

    