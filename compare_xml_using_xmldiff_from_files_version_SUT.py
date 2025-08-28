import os
import argparse
from utils import run_comparaison
from datetime import datetime
import time

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

    total_count = {}
    file_count = 0
    total_difference = 0
    number_of_files_with_difference = 0
    total_suspicion = 0
    number_of_files_with_suspicion = 0


    # start timer
    start_time = time.time()

    for gen_file, ref_file in zip(generated_files, reference_files):
        gen_path = os.path.join(args.generated_folder, gen_file)
        ref_path = os.path.join(args.reference_folder, ref_file)

        result = run_comparaison(ref_path, gen_path, args.config)
        file_count +=1
        difference =  result.get("Added", 0)+result.get("Deleted", 0)+result.get("Type Mismatch", 0)+result.get("Different", 0)
        if difference > 0:
            number_of_files_with_difference += 1
        if result.get("Suspected", 0) > 0:
            number_of_files_with_suspicion += 1
        for key in result:
            total_count[key] = total_count.get(key,0) + result[key]

    # end timer
    end_time = time.time()

    # calculate duration
    total_execution_time = end_time - start_time

    now = datetime.now()
    date_time_end_of_campagne = f"Date: {now.strftime('%Y-%m-%d')} Time: {now.strftime('%H:%M:%S')}"
    total_difference += total_count.get("Added", 0)+total_count.get("Deleted", 0)+total_count.get("Type Mismatch", 0)+total_count.get("Different", 0)


    print(f'Nombre de fichiers traités : {file_count}')
    print(f'Statistiques de la campagne :')
    print(f'\t{total_difference} différences détectées dans {number_of_files_with_difference} fichiers ')
    print(f'\t\tAdded: {total_count.get("Added", 0)}')
    print(f'\t\tDeleted: {total_count.get("Deleted", 0)}')
    print(f'\t\tType Mismatch: {total_count.get("Type Mismatch", 0)}')
    print(f'\t\tDifferent: {total_count.get("Different", 0)}')
    print(f'\t{total_count.get("Suspected", 0)} équivalences suspectées dans {number_of_files_with_suspicion} fichiers ')
    print(f"Durée d'exécution: {total_execution_time} (secondes)")
    print(f"Fin de la comparaison : {date_time_end_of_campagne}")
