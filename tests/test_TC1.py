import semanticComparaison
from semanticComparaison import compare_xml_files


def test_TC1():
    compare_xml_files("referenceMessages/file1.xml", "generatedMessages/file2.xml")
