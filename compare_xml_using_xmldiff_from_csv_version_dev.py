import csv
from utils import run_comparaison
import json

from lxml import etree
from xmldiff import main, formatting, actions
import re


def read_relevant_test_cases(csv_file_path):
    test_cases = []

    with open(csv_file_path, mode='r',encoding="utf-8", newline='') as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')

        for row in reader:
            # Skip rows that are too short or don't start with "TC"
            if not row or not row[0].strip().startswith("TC"):
                continue

            #print(row)

            # Extract the relevant fields
            test_case_id = row[0].strip()
            case_label = row[1].strip()
            description = row[2].strip()
            xml_ref = row[3].strip()
            xml_gen = row[4].strip()
            expected_result = row[7].strip()


            test_cases.append({
                "id": test_case_id,
                "label": case_label,
                "description": description,
                "xml_reference": xml_ref,
                "xml_generated": xml_gen,
                "expected_result": expected_result,
            })

    return test_cases

csv_file_path = "./tests/cahier_de_recette.csv"

tests = read_relevant_test_cases(csv_file_path)

for test in tests:
    print("---------------------------------")
    print("Running test case:")
    print(test["label"])

    if (test["label"] == "9a- Existence + valeur unique" or  test["label"] == "9c- Valeur + exclusion de champ"):
        continue

    #file1 = f"reference-{test["id"]}.xml"
    file1 = f"reference.xml"
    with open(file1, "w", encoding="utf-8") as file:
        file.write(test["xml_reference"])
    #file2 = f"generates-{test["id"]}.xml"
    file2 = f"generates.xml"
    with open(file2, "w", encoding="utf-8") as file:
        file.write(test["xml_generated"])

    run_comparaison(file1,file2, "config.json")
