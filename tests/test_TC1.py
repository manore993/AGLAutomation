import pytest
from AGLAutomation.semantic_comparaison import compare_xml_files
import csv


def test_identical_files(capsys):
    compare_xml_files("referenceMessages/file1.xml", "referenceMessages/file1.xml")
    output = capsys.readouterr().out
    assert output == ""

def test_TC1(capsys):
    compare_xml_files("referenceMessages/file1.xml", "generatedMessages/file2.xml")
    output = capsys.readouterr().out
    assert output != ""
