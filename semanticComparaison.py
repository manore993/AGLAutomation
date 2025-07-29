import xml.etree.ElementTree as ET
from collections import Counter
import hashlib

def parse_xml(file_path):
    tree = ET.parse(file_path)
    return tree.getroot()

def normalize_text(text):
    return (text or '').strip()

def hash_element(elem):
    """
    Recursively create a hash of an element's structure, attributes, text, and children.
    Used for deep comparison and deduplication.
    """
    h = hashlib.sha256()
    h.update(elem.tag.encode())
    for key in sorted(elem.attrib):
        h.update(f"{key}={elem.attrib[key]}".encode())
    h.update(normalize_text(elem.text).encode())

    for child in elem:
        h.update(hash_element(child).encode())

    return h.hexdigest()

def get_element_signature(elem):
    """
    Return a simplified signature of an element for comparison.
    """
    return {
        "tag": elem.tag,
        "attrib": dict(sorted(elem.attrib.items())),
        "text": normalize_text(elem.text),
        "hash": hash_element(elem)
    }

def compare_children_equivalence(e1, e2, path="/"):
    current_path = f"{path}/{e1.tag}"

    # Collect all children hashes
    children1 = list(e1)
    children2 = list(e2)

    sigs1 = [get_element_signature(child) for child in children1]
    sigs2 = [get_element_signature(child) for child in children2]

    hashes1 = [sig["hash"] for sig in sigs1]
    hashes2 = [sig["hash"] for sig in sigs2]

    count1 = Counter(hashes1)
    count2 = Counter(hashes2)

    all_hashes = set(hashes1 + hashes2)

    for h in all_hashes:
        c1 = count1.get(h, 0)
        c2 = count2.get(h, 0)

        if c1 > 1 or c2 > 1:
            print(f"Duplicate element at {current_path}: hash={h[:8]} appears {c1} times in file1, {c2} times in file2")

        if c1 != c2:
            print(f"Element count mismatch at {current_path}: hash={h[:8]} appears {c1} times in file1 vs {c2} in file2")

    # Check for same content but different order
    if hashes1 != hashes2 and sorted(hashes1) == sorted(hashes2):
        print(f"Elements at {current_path} are equivalent but in different order")

    # Recurse for matching elements
    matched = zip(children1, children2) if len(children1) == len(children2) else []
    for c1, c2 in matched:
        compare_children_equivalence(c1, c2, path=current_path)

def compare_xml_files(file1, file2):
    root1 = parse_xml(file1)
    root2 = parse_xml(file2)

    # First check root tags
    if root1.tag != root2.tag:
        print(f"Root tag mismatch: {root1.tag} != {root2.tag}")
        return

    # Then do deep comparison of children
    compare_children_equivalence(root1, root2)

#if __name__ == '__semanticComparaison__':
# Example usage
compare_xml_files("file1.xml", "file2.xml")
