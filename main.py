import sys
import xml.etree.ElementTree as ET

# Parse the XML file
def parse_xml(file_path):
    tree = ET.parse(file_path)
    return tree.getroot()

# Replace with your XML file name
#file_path = 'example1.xml'

#root = parse_xml(file_path)

# Print the root tag and its attributes (if any)
#print(f"Root tag: {root.tag}, attributes: {root.attrib}")

# Loop through child elements
#for child in root:
    #print(f"Tag: {child.tag}, Attributes: {child.attrib}, Text: {child.text.strip() if child.text else 'None'}")

def compare_elements(e1, e2, path="/"):
    if e1.tag != e2.tag:
        print(f"Tag mismatch at {path}: '{e1.tag}' != '{e2.tag}'")

    if e1.attrib != e2.attrib:
        print(f"Attribute mismatch at {path}: {e1.attrib} != {e2.attrib}")

    t1 = (e1.text or '').strip()
    t2 = (e2.text or '').strip()

    different_value_is_allowed = e1.tag == "MessageUUID"

    if t1 != t2 and not different_value_is_allowed:
        print(f"Text mismatch at {path}: '{t1}' != '{t2}'")

    if len(e1) != len(e2):
        print(f"Children count mismatch at {path}: {len(e1)} != {len(e2)}")

    # Recursively compare children
    for i, (child1, child2) in enumerate(zip(e1, e2), start=1):
        child_path = f"{path}/{e1.tag}[{i}]"
        compare_elements(child1, child2, path=child_path)



if __name__ == '__main__':
    # Example usage:
    file1 = sys.argv[1]
    file2 = sys.argv[2]

    root1 = parse_xml(file1)
    root2 = parse_xml(file2)

    compare_elements(root1, root2)