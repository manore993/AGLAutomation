import os
import argparse
from utils import run_comparaison

# Generate exe
# working dir = AGLAutomation
# pyinstaller --onefile compare_xml_using_xmldiff_from_files_version_SUT.py --paths=.

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compare generated and reference XML messages.")
    parser.add_argument(
        "--generated_folder",
        default="tests/generatedMessages",
        help="Path to the folder containing generated files (default: tests/generatedMessages)"
    )
    parser.add_argument(
        "--reference_folder",
        default="tests/referenceMessages",
        help="Path to the folder containing reference files (default: tests/referenceMessages)"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the configuration file (default: config.json)"
    )

    args = parser.parse_args()

    generated_files = sorted(os.listdir(args.generated_folder))
    reference_files = sorted(os.listdir(args.reference_folder))

    for gen_file, ref_file in zip(generated_files, reference_files):
        gen_path = os.path.join(args.generated_folder, gen_file)
        ref_path = os.path.join(args.reference_folder, ref_file)

        run_comparaison(ref_path, gen_path, args.config)
