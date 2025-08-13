import csv
from lxml import etree
from xmldiff import main, formatting, actions


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
    #file1 = f"reference-{test["id"]}.xml"
    file1 = f"reference.xml"
    with open(file1, "w", encoding="utf-8") as file:
        file.write(test["xml_reference"])
    #file2 = f"generates-{test["id"]}.xml"
    file2 = f"generates.xml"
    with open(file2, "w", encoding="utf-8") as file:
        file.write(test["xml_generated"])

    # Parse XML files
    tree1 = etree.parse(file1)
    tree2 = etree.parse(file2)

    # Run xmldiff in 'diff_files' mode to get structured actions
    ops = main.diff_files(file1, file2, diff_options={'F': 0.1})  # F=similarity threshold

    def get_type(text):
        if len(text) > 1 and text[0] == '"':
            return "string"
        return "int"



    # Custom message map
    def custom_message(op):
        if isinstance(op, actions.DeleteNode):
            return f'Missing "{op.node}" from file2'
        elif isinstance(op, actions.InsertNode):
            return f'Unexpected "{op.tag}" in file2'
        elif isinstance(op, actions.UpdateTextIn):
            new_value = op.text
            result_old_values = tree1.xpath(op.node)
            old_value = result_old_values[0].text if len(result_old_values)>0 else ""
            if get_type(new_value) != get_type(old_value):
                return f'Type mismatched at "{op.node}" : file1 has {get_type(old_value)} and file2 has {get_type(new_value)}'
            return f'Value changed in "{op.node}" from {old_value} to {new_value}'
        return None


    # Display custom messages
    for op in ops:
        msg = custom_message(op)
        if msg:
            print(msg)
