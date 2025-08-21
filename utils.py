import json

from lxml import etree
from xmldiff import main, formatting, actions
import re

def get_type(text):
    if len(text) > 1 and text[0] == '"':
        return "string"
    return "int"


# Custom message map
def custom_message(reference_path:str, generated_path:str, op, inserted_nodes, suspicion_nodes, deleted_nodes, ignored_tags, ignored_values, tree1):
    if isinstance(op, actions.MoveNode):
        parent_path = '/'.join(op.node.split('/')[0:-1]).strip()
        if parent_path in suspicion_nodes:
            return None
        #add parent_path in suspicion_nodes first time it captures for the same parent, to ignore next time it appears in the same parent,
        # because we want to inform only once even if there are more than one change of place of nodes for the same immediate parent.
        suspicion_nodes.add(parent_path)
        return(f'Changed order but equivalent for the elements of {parent_path}')

    if isinstance(op, actions.DeleteNode):
        parent_path = '/'.join(op.node.split('/')[0:-1])

        if parent_path in deleted_nodes:
            return None

        return f'Missing "{op.node}" from file2 {generated_path}'
    elif isinstance(op, actions.InsertNode):
        inserted_nodes.add(op.tag)
        return f'Unexpected "{op.tag}" in file2 {generated_path}'
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
            return f'Type mismatched at "{op.node}" : file1 {reference_path} has {get_type(old_value)} and file2 {generated_path} has {get_type(new_value)}'
        if new_value.strip() == old_value.strip():
            return None

        path_to_test_for_ignore_values = op.node.split('[')[0]
        #print(f'path to test for ignored values {path_to_test_for_ignore_values}')
        #print(f'old_value {old_value} new_value {new_value}')

        for value in ignored_values:
            #print(f'Value_path in ignored_values {value["path"]} value_pattern in ignored_values {value["patterns"]}')
            if path_to_test_for_ignore_values == value["path"]:
                #value_to_be_same = new_value.split('[')[0]
                value_to_be_ignored = "[" + new_value.split('[')[1]
                if value_to_be_ignored.strip() == value["patterns"].strip():
                    print("None")
                #print(f'Value to be same {value_to_be_same} value to be ignored {value_to_be_ignored}')

        ignored_parts_for_this_path = [] # TODO Find from config
        #if removed_ignored_part(new_value.strip(), ignored_parts_for_this_path).strip() == old_value.strip():
        #    return None
        return f'Value changed in "{op.node}" from {old_value} in file1 {reference_path} to {new_value} in file2 {generated_path}'
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
    # ignored_tags = ["UUID", "TS", "SessionID"]
    # deleted_nodes = set()
    # Display custom messages
    for op in ops:
        msg = custom_message(reference_path, generated_path, op, inserted_nodes, deleted_nodes, suspicion_nodes, ignored_tags, ignored_values, tree1)
        if msg:
            print(msg)
