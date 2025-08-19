import csv
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


def get_type(text):
    if len(text) > 1 and text[0] == '"':
        return "string"
    return "int"


# Custom message map
def custom_message(op, inserted_nodes, deleted_nodes, ignored_tags, tree1):
    if isinstance(op, actions.DeleteNode):
        parent_path = '/'.join(op.node.split('/')[0:-1])

        if parent_path in deleted_nodes:
            return None

        return f'Missing "{op.node}" from file2'
    elif isinstance(op, actions.InsertNode):
        inserted_nodes.add(op.tag)
        return f'Unexpected "{op.tag}" in file2'
    elif isinstance(op, actions.UpdateTextIn):
        parent_path = op.node.split('/')[-1].split('[')[0]
        # print(f' parent ath is : ', parent_path)
        # print(f' node is : ', op.node)

        for tag in ignored_tags:
            pattern = re.compile(fr'{tag}', re.IGNORECASE)
            # print(pattern.search(parent_path))
            if pattern.search(parent_path) is not None:
                return None

        if parent_path in inserted_nodes or parent_path in deleted_nodes:
            return None
        new_value = op.text
        result_old_values = tree1.xpath(op.node)
        old_value = result_old_values[0].text if len(result_old_values) > 0 else ""
        if get_type(new_value) != get_type(old_value):
            return f'Type mismatched at "{op.node}" : file1 has {get_type(old_value)} and file2 has {get_type(new_value)}'
        if new_value.strip() == old_value.strip():
            return None
        return f'Value changed in "{op.node}" from {old_value} to {new_value}'
    return None


def find_deletes(ops):
    result = set()
    for op in ops:
        if isinstance(op, actions.DeleteNode):
            current_path = op.node.split('[')[0]
            result.add(current_path)
    return result


def load_config(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data

def run_comparaison(reference_path:str, generated_path:str, config_path:str):
    # Parse XML files
    tree1 = etree.parse(file1)
    tree2 = etree.parse(file2)

    # Run xmldiff in 'diff_files' mode to get structured actions
    ops = main.diff_files(reference_path, generated_path, diff_options={'F': 0.1})  # F=similarity threshold

    # ops.sort(key=lambda x: 0 if isinstance(x, actions.DeleteNode) or isinstance(x, actions.InsertNode) else 1)

    config = load_config(config_path)
    deleted_nodes = find_deletes(ops)
    inserted_nodes = set()
    ignored_tags = config["ignored_tags"]
    # ignored_tags = ["UUID", "TS", "SessionID"]
    # deleted_nodes = set()
    # Display custom messages
    for op in ops:
        msg = custom_message(op, inserted_nodes, deleted_nodes, ignored_tags, tree1)
        if msg:
            print(msg)


for test in tests:
    print("---------------------------------")
    print("Running test case:")
    print(test["label"])

    if (test["label"] == "9a- Existence + valeur unique" or  test["label"] == "9c- Valeur + exclusion de champ"
            or  test["label"] == "10b – Exclusion de tag commentaire variable"):
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
