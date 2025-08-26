import os

from utils import run_comparaison

# folders
generated_folder = "tests/generatedMessages"
reference_folder = "tests/referenceMessages"

# get sorted file lists so matching is consistent
generated_files = sorted(os.listdir(generated_folder))
reference_files = sorted(os.listdir(reference_folder))

# iterate over pairs
for gen_file, ref_file in zip(generated_files, reference_files):
    gen_path = os.path.join(generated_folder, gen_file)
    ref_path = os.path.join(reference_folder, ref_file)

    # here you can call your comparison function
    #print(f"Comparing file {gen_file} with file {ref_file}")
    #print(f"Comparing path {gen_path} with path {ref_path}")

    run_comparaison(ref_path,gen_path, "config.json")

