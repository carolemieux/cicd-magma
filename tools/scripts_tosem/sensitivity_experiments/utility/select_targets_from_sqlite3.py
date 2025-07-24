import os
import random
import subprocess


def get_num_files_modified(patch_path):
    modified_files = set()
    with open(patch_path, 'r') as file:
        for line in file:
            if line.startswith('---') or line.startswith('+++'):
                # omit checking /dev/null as the patch files in magma do not include such lines
                modified_files.add(line)
    num_of_files = len(modified_files)
    # print(f'{patch_path}: {num_of_files} files modified')
    return  num_of_files


def process_mean_num_files_modified(patch_base_dir):
    average_loc_modified_lst = []
    for lib_dir in os.listdir(patch_base_dir):
        # avoid processing libs with the underscore extension
        if '_' not in lib_dir:
            lib_path = os.path.join(patch_base_dir, lib_dir, 'patches/bugs')
            if os.path.isdir(lib_path):
                num_of_patches = 0
                sum_of_modified_lines = 0
                for patch_file in os.listdir(lib_path):
                    patch_path = os.path.join(lib_path, patch_file)
                    if os.path.isfile(patch_path):
                        num_of_patches += 1
                        sum_of_modified_lines += get_num_files_modified(patch_path)
                average_loc_modified = sum_of_modified_lines / num_of_patches
                average_loc_modified_lst.append(average_loc_modified)
                print(f'{lib_dir}: {sum_of_modified_lines}, {average_loc_modified}')
    print(average_loc_modified_lst)
    print(f'The average number of files modified in patches is: {sum(average_loc_modified_lst) / len(average_loc_modified_lst)}')


def select_from_sqlite3(repo_dir, output_path, file_limit=2, loc_lower_limit=10, loc_upper_limit=100):
    file_extensions = ('.c', '.h', '.cpp', '.cc')
    filtered_files = []
    for path, _, file_names in os.walk(repo_dir):
        for file_name in file_names:
            if file_name.endswith(file_extensions):
                filtered_files.append(os.path.join(path, file_name))

    results = {}
    if filtered_files:
        random_files = random.sample(filtered_files, min(file_limit, len(filtered_files)))
        for random_file in random_files:
            # for short command, use check_output for faster processing
            if loc_upper_limit > loc_lower_limit:
                code_chunk_size = random.choice(range(loc_lower_limit, loc_upper_limit+1))
                num_of_lines = int(subprocess.check_output(['wc', '-l', random_file]).split()[0])
                random_numbers = random.sample(range(1, num_of_lines + 1), min(code_chunk_size, num_of_lines))
                print(f'{random_file}: {random_numbers}')
                assert code_chunk_size == len(random_numbers)
                loc_upper_limit -= code_chunk_size
                file_name = '/'.join(random_file.split('/')[5:])
                results[file_name] = random_numbers
    else:
        print(f'No files with the extension found.')

    print(results)
    with open(output_path, 'w') as file:
        for file_name, lines in results.items():
            for line in lines:
                file.write(f'{file_name}:{line}\n')


if __name__ == "__main__":
    # select_from_sqlite3('/home/huicongh/temp/sqlite3', './SQL018')
    # select_from_sqlite3('/home/huicongh/temp/sqlite3', './SQL020')
    # process_mean_num_files_modified('/home/huicongh/ContinuousFuzzBench/targets')
    size_limit = 100
    random.seed(57)

    random_lines = random.sample(range(1, 235766 + 1), random.choice(range(1, size_limit+1)))
    with open('./SQL018', 'w') as file:
        for line in random_lines:
            file.write(f'sqlite3.c:{line}\n')
    random.seed(43)
    random_lines = random.sample(range(1, 235766 + 1), random.choice(range(1, size_limit+1)))
    with open('./SQL020', 'w') as file:
        for line in random_lines:
            file.write(f'sqlite3.c:{line}\n')
