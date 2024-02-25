import os
import shutil
import subprocess

def submission_file_path(instance, filename):
    return f"submissions/{instance.problem.name}/{instance.user_id}/{instance.created_at:%Y-%m-%d_%H-%M-%S}.asm"

def problem_test_folder_path(instance):
    return os.path.dirname(instance.test_file.path)

def problem_test_file_path(instance, filename):
    return f"problems/{instance.name}/{filename}"

def extract_zip(input_zip, extract_to):
    from zipfile import ZipFile
    with ZipFile(input_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def test_code(code_file, problem):
    temp_dir = f"temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    code_file = os.path.join('media', code_file.path)
    subprocess.run(f'nasm -f elf64 "{code_file}" -o "{temp_dir}/code.o"', shell=True, check=True)
    subprocess.run(f"ld {temp_dir}/code.o -e _start -o {temp_dir}/a.out", shell=True, check=True)
    test_cases_path = f"media/problems/{problem.name}"
    results = []
    for input_file_name in os.listdir(f"{test_cases_path}/input"):
        try:
            input_file_path = os.path.join(test_cases_path, "input", input_file_name)
            output_file_path = os.path.join(test_cases_path, "output", f"output{input_file_name.split('input')[1]}")
            with open(input_file_path, 'r') as input_file, open(f"{temp_dir}/output.txt", 'w') as output_file:
                try:
                    subprocess.run([f"{temp_dir}/a.out"], stdin=input_file, stdout=output_file, timeout=problem.timeout)
                except subprocess.TimeoutExpired:
                    results += [2]
                    continue
                
            with open(output_file_path, 'r') as expected_file, open(f"{temp_dir}/output.txt", 'r') as actual_file:
                expected_output = expected_file.read()
                actual_output = actual_file.read()
                if expected_output == actual_output:
                    results += [0]
                else:
                    results += [1]
        except Exception as e:
            results += [3]

    return results

def read_code_file(code_file):
    code_content = ""
    if code_file:
        with code_file.open() as code_file:
            code_content = code_file.read().decode('utf-8')
    return code_content

def delete_folder(folder_path):
    shutil.rmtree(folder_path)
