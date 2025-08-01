# What This Script Does
#   Compares XML files semantically.
#   Uses a recursive hash-based signature for each element.
#   Detects:
#       Duplicates (same element repeated in one file).
#       Missing elements (one file has an extra or missing node).
#       Same elements in different order.
#       Ignores order if contents are equal.

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
    print(children1)
    children2 = list(e2)

    sigs1 = [get_element_signature(child) for child in children1]
    sigs2 = [get_element_signature(child) for child in children2]

    hash_to_elem1 = {sig["hash"]: elem for sig, elem in zip(sigs1, children1)}
    hash_to_elem2 = {sig["hash"]: elem for sig, elem in zip(sigs2, children2)}

    #hashes1 and hashes2 are lists of hashes of child elements (created earlier with a hash function that recursively
    # captures the structure of each child).
    hashes1 = [sig["hash"] for sig in sigs1]
    hashes2 = [sig["hash"] for sig in sigs2]

    #Counter(...) gives you a dictionary-like object with element hash as the key and the number of times it appears as the value.
    count1 = Counter(hashes1)
    count2 = Counter(hashes2)

    #Combines both lists of hashes and makes a set: this gets every unique child element hash across both XML files.
    #This ensures you're comparing every element type that appears in either file.
    all_hashes = set(hashes1 + hashes2)

    for h in all_hashes:
        # For each unique hash h, look up how many times it appears in:
        #   c1: file 1
        #   c2: file 2
        c1 = count1.get(h, 0)
        c2 = count2.get(h, 0)

        # Todo:Noeud manquant et Noeud supplementaire Patrice(2 et 3) Penda(TC4 - TC7)
        # Todo:Convert hash into something understandable
        #If any element hash appears more than once in either file, it's considered a duplicate.
        # You print a warning including the path and a short version of the hash (first 8 chars for readability).
        if c1 > 1 or c2 > 1:
            print(f"Duplicate element at {current_path}: hash={h[:8]} appears {c1} times in file1, {c2} times in file2")
        #If the same element appears a different number of times between files, it's a mismatch.
        #This can indicate:
        #   Missing elements
        #   Extra duplicates in one file
        #   Todo:Patrice(11-12) Penda(T26-T29)
        if c1 != c2:
            # Try to get element from file1, fallback to file2
            element = hash_to_elem1.get(h)
            if element is None:
                element = hash_to_elem2.get(h)
            xml_str = ET.tostring(element, encoding='unicode').strip()
            print(f"Duplicate element at {current_path}: appears {c1} times in file1, {c2} times in file2:\n{xml_str}")
            print(f"Element count (Missing or extra child ) mismatch at {current_path}: hash={h[:8]} appears {c1} times in file1 vs {c2} in file2")

    # Check for same content but different order
    # This checks if:
        # The elements are not in the same order, but
        # The content is equivalent (same hashes, just rearranged)
    # This is the key line that allows out-of-order elements but still warns the user.
    # ✅ If you care about structure but not order — this is what you want.
    # Todo:Convert hash into something understandable
    if hashes1 != hashes2 and sorted(hashes1) == sorted(hashes2):
        print(f"Elements at {current_path} are equivalent but in different order")

    # Recurse for matching elements
    # This recursively compares each matching pair of children — only if both sides have the same number of child elements.
    # Todo Patrice(11-12) Penda(T26-T29)
    # If the number differs, we skip the recursion because we can't safely align child1[i] with child2[i].
    # This is a simple way to avoid misaligned comparisons in mismatched trees.

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
compare_xml_files("referenceMessages/file1.xml", "generatedMessages/file2.xml")
