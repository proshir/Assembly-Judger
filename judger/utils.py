import os
import re
import shutil
import subprocess
import tempfile

def submission_file_path(instance, filename):
    return f"submissions/{instance.problem.name}/{instance.user_id}/{instance.created_at:%Y-%m-%d_%H-%M-%S}.asm"

def problem_test_folder_path(instance):
    return os.path.dirname(instance.test_file.path)

def get_problem_folder(name):
    return f"media/problems/{name}"

def get_submissions_folder(name):
    return f"media/submissions/{name}"

def problem_test_file_path(instance, filename):
    return f"problems/{instance.name}/{filename}"

def extract_zip(input_zip, extract_to):
    from zipfile import ZipFile
    with ZipFile(input_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

import logging

def sort_key(filename):
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    else:
        return float('inf') 


def test_code(code_file, problem):
    temp_dir = tempfile.mkdtemp(prefix="temp_", dir="temp")
    try:
        code_file_path = os.path.join('media', code_file.path)
        o_path = os.path.join(temp_dir, "code.o")
        subprocess.run(f'nasm -f elf64 "{code_file_path}" -o "{o_path}"', shell=True, check=True)
        a_path = os.path.join(temp_dir, 'a.out')
        subprocess.run(f"ld {o_path} -e _start -o {a_path}", shell=True, check=True)
        
        test_cases_path = f"media/problems/{problem.name}"
        results = []

        for input_file_name in sorted(os.listdir(os.path.join(test_cases_path, 'input')), key=sort_key):
            try:
                input_file_path = os.path.join(test_cases_path, "input", input_file_name)
                output_file_path = os.path.join(test_cases_path, "output", f"output{input_file_name.split('input')[1]}")
                output_act = os.path.join(temp_dir, 'output.txt')

                completed_process = subprocess.run(a_path, input=open(input_file_path, 'r').read(), 
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                                timeout=problem.timeout, text=True)
                
                if completed_process.returncode == 0:
                    with open(output_act, 'w') as output_file:
                        output_file.write(completed_process.stdout)
                else:
                    raise Exception("Error occurred:", completed_process.stderr)

                with open(output_file_path, 'r') as expected_file, open(output_act, 'r') as your_out_file:
                    expected_output = expected_file.read()
                    your_output = your_out_file.read()
                    if expected_output == your_output:
                        results += [0]
                    else:
                        results += [1]

            except subprocess.TimeoutExpired:
                print("Subprocess timed out.")
                results += [2] 
            
            except Exception as e:
                logging.error("Error at testing code: %s", str(e))
                results += [3]
    finally:
        shutil.rmtree(temp_dir)
    return results

def read_code_file(code_file):
    code_content = ""
    if code_file:
        with code_file.open() as code_file:
            code_content = code_file.read().decode('utf-8')
    return code_content

def delete_folder(folder_path):
    shutil.rmtree(folder_path)

def delete_tests(folder_path):
    input_folder_path = os.path.join(folder_path, 'input')
    output_folder_path = os.path.join(folder_path, 'output')

    if os.path.exists(input_folder_path):
        shutil.rmtree(input_folder_path)
    
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)