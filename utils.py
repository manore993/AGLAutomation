import json
import csv
import os
from datetime import datetime

from lxml import etree
from xmldiff import main, formatting, actions
import re

def get_type(text):
    if len(text) > 1 and text[0] == '"':
        return "string"
    return "int"

def load_config(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


def find_deletes(ops):
    result = set()
    for op in ops:
        if isinstance(op, actions.DeleteNode):
            current_path = op.node.split('[')[0]
            result.add(current_path)
    return result

def run_comparaison(reference_path:str, generated_path:str, config_path:str):
    # Parse XML files
    tree1 = etree.parse(reference_path)
    tree2 = etree.parse(generated_path)

    # Run xmldiff in 'diff_files' mode to get structured actions
    ops = main.diff_files(reference_path, generated_path, diff_options={'F': 0.1})  # F=similarity threshold

    # ops.sort(key=lambda x: 0 if isinstance(x, actions.DeleteNode) or isinstance(x, actions.InsertNode) else 1)

    config = load_config(config_path)
    deleted_nodes = find_deletes(ops)
    suspicion_nodes = set()
    inserted_nodes = set()
    ignored_tags = config["ignored_tags"]
    ignored_values = config["ignored_values"]

    type_counts = {}
    details = []
    # ignored_tags = ["UUID", "TS", "SessionID"]
    # deleted_nodes = set()
    # Display custom messages
    for op in ops:
        msg = custom_message(reference_path, generated_path, op, inserted_nodes, suspicion_nodes,deleted_nodes, ignored_tags, ignored_values, tree1)
        if msg:
            result_type, detail = msg
            type_counts[result_type] = type_counts.get(result_type, 0) + 1
            details.append(f'{result_type} {detail}')
            #write_comparison_result(reference_path, generated_path, msg)
            #write_comparison_result(reference_path, generated_path, type_counts, details, delimiter)
            #print(f'Type_count: {type_counts}')
            #print(msg)
    #print(f'Type_count: {type_counts}')
    write_comparison_result(reference_path, generated_path, type_counts, details, config, delimiter = ";")
    return type_counts

# Custom message map
def custom_message(reference_path:str, generated_path:str, op, inserted_nodes, suspicion_nodes, deleted_nodes, ignored_tags, ignored_values, tree1):
    if isinstance(op, actions.MoveNode):
        parent_path = '/'.join(op.node.split('/')[0:-1]).strip()
        if parent_path in suspicion_nodes:
            return None
        #add parent_path in suspicion_nodes first time it captures for the same parent, to ignore next time it appears in the same parent,
        # because we want to inform only once even if there are more than one change of place of nodes for the same immediate parent.
        suspicion_nodes.add(parent_path)
        #return(f'Changed order but equivalent for the elements of {parent_path}')
        return ("Suspected",
                f'Changed order but equivalent for the elements of {parent_path}')


    if isinstance(op, actions.DeleteNode):
        parent_path = '/'.join(op.node.split('/')[0:-1])

        if parent_path in deleted_nodes:
            return None

        #return (f'Missing {op.node} from file2 {generated_path}')
        return ("Deleted",
                f'Missing {op.node} from file2 {generated_path}')


    elif isinstance(op, actions.InsertNode):
        #print("-------------")
        parent_tag = (op.target.split('/')[-1]).split('[')[0]
        #print(f'parent_tag: {parent_tag}')
        #print(f'inserted_nodes: {inserted_nodes}')
        if parent_tag in inserted_nodes:
             return None
        inserted_nodes.add(op.tag)
        #print(f'op.target {op.target}')
        #print(f'inserted_nodes: {inserted_nodes}')
        #print("-------------")
        #return f'Unexpected "{op.tag}" in file2 {generated_path}'
        return ("Added",
                f'Unexpected "{op.tag}" in file2 {generated_path}')



    elif isinstance(op, actions.UpdateTextIn):
        parent_path = op.node.split('/')[-1].split('[')[0]
        #print(f' parent path is : ', parent_path)
        #print(f' node is : ', op.node)
        for tag in ignored_tags:
            pattern = re.compile(fr'{tag}', re.IGNORECASE)
            #print(pattern.search(parent_path))
            if pattern.search(parent_path) is not None:
                #print(pattern.search(parent_path).group())
                #return f"{pattern.search(parent_path).group()} ignored - Test passed"
                return ("Ignore Pattern",
                        f"{pattern.search(parent_path).group()} ignored - Test passed")


        #op.node.split('/')[-2] in inserted_nodes (to check also that the child of missing parent is not checked for missing value)
        if parent_path in inserted_nodes or op.node.split('/')[-2] in inserted_nodes or parent_path in deleted_nodes:
            return None
        new_value = op.text
        result_old_values = tree1.xpath(op.node)
        old_value = result_old_values[0].text if len(result_old_values) > 0 else ""
        if get_type(new_value) != get_type(old_value):
            #return f'Type mismatched at "{op.node}" : file1 {reference_path} has {get_type(old_value)} and file2 {generated_path} has {get_type(new_value)}'
            return ("Type Mismatch",
                    f'Type mismatched at "{op.node}" : file1 {reference_path} has {get_type(old_value)} and file2 {generated_path} has {get_type(new_value)}')

        if new_value.strip() == old_value.strip():
            #return "Same value - Test passed"
            #return ("Same value",
                    #f'Test passed')
            return None

        path_to_test_for_ignore_values = op.node.split('[')[0]
        #print(f'path to test for ignored values {path_to_test_for_ignore_values}')
        #print(f'old_value {old_value} new_value {new_value}')

        for value in ignored_values:
            #print(f'Value_path in ignored_values {value["path"]} value_pattern in ignored_values {value["patterns"]}')
            if path_to_test_for_ignore_values == value["path"]:
                value_to_be_same = new_value.split('[')[0]
                #value_to_be_ignored = "[" + new_value.split('[')[1]
                new_value_clean = new_value.replace(value["patterns"].strip(), "")
                if old_value.strip() == new_value_clean.strip():
                    #return f"Test passed"
                    #return ("Test Green",
                            #"Test passed")
                    return None

                #print(f'Value to be same {value_to_be_same} value to be ignored {value_to_be_ignored}')

        #return f'Value changed in "{op.node}" from {old_value} in file1 {reference_path} to {new_value} in file2 {generated_path}'
        return ("Different",
                f'Value changed in "{op.node}" from {old_value} in file1 {reference_path} to {new_value} in file2 {generated_path}')

    return None

csv_file_name = None

def get_csv_file_name():
    """Generates and stores a CSV file name with date and time if not already created."""
    global csv_file_name
    if csv_file_name is None:
        now = datetime.now()
        csv_file_name = f"TNR_{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}.csv"
    return csv_file_name

#def write_comparison_result(reference_file: str, generated_file: str, comparison_result: tuple):
def write_comparison_result(reference_file: str, generated_file: str, type_counts: dict, details: list, config: dict, delimiter: str = ";"):
    """
    Writes comparison results to a CSV file without overwriting previous data.


    Parameters:
    reference_file (str): Reference Message File Name
    generated_file (str): Generated message File Name
    output_message (str): Comparison Output Message
    detailed_message (str): Comparison Output Details Message
    """

    #comparison_type, comparison_message = comparison_result
    detail_messages = delimiter.join(details)

    file_name = get_csv_file_name()
    file_exists = os.path.isfile(file_name)


    # Open the file in append mode
    with open(file_name, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)


        # Write header if the file is new
        # if not file_exists:
        #     writer.writerow([
        #     "Reference Message File Name",
        #     "Generated message File Name",
        #     "Comparaison Output Message (Type)",
        #     "Comparaison Output detailes message"
        #     ])
        # if not file_exists:
        #     writer.writerow([
        #         "Reference File",
        #         "Generated File",
        #         "Nb Added",
        #         "Nb Deleted",
        #         "Nb Suspected",
        #         "Nb Ignore Pattern",
        #         "Nb Type Mismatch",
        #         "Nb Different",
        #         "Details"
        #     ])

        #print(f'Type count in write_comparaison_result: {type_counts}')
        print_console = [
            reference_file,
            generated_file,
            type_counts,
            config
        ]
        #print(print_console)

        # Write the data
        #writer.writerow([reference_file, generated_file,comparison_type, comparison_message])
        # writer.writerow([
        #     reference_file,
        #     generated_file,
        #     type_counts.get("Added", 0),
        #     type_counts.get("Deleted", 0),
        #     type_counts.get("Suspected", 0),
        #     type_counts.get("Ignore Pattern", 0),
        #     type_counts.get("Type Mismatch", 0),
        #     type_counts.get("Different", 0),
        #     detail_messages
        # ])


