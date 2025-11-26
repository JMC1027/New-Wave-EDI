import json
import csv
import traceback
#from generateDentalX12_Batch import generate_dental_x12_batch
from generateDentalX12_Single import generate_dental_x12_single


def generate():
    try:
        json_file_path = "Output/JSON_Output/mockedDentalClaim.json"
        generate_dental_x12_single(json_file_path)

        #json_file_path = "Output/JSON_Output/mockedDentalClaim.json"
        #generate_dental_x12_single(json_file_path)


    except Exception as e:
        print(f"Failed to generate X12 file: {e}")
        traceback.print_exc()

generate()


    
