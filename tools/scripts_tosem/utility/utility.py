import os
import random

def select_50_random_benchmarks():
    benchmarks = ['libpng', 'libtiff', 'libxml2', 'poppler', 'openssl', 'sqlite3', 'php', 'libsndfile']
    num_of_bugs = [7, 14, 17, 22, 20, 20, 16, 18]
    num_of_drivers = [1, 1, 2, 1, 6, 1, 4, 1]

    selected_benchmarks = []
    for i in range(len(benchmarks)):
        for j in range(num_of_bugs[i]):
            for k in range(num_of_drivers[i]):
                selected_benchmarks.append(benchmarks[i] + "_" + str(j + 1) + "_" + str(k + 1))

    random.seed(42)
    selected_benchmarks = random.sample(selected_benchmarks, 50)
    sorted_selected_benchmarks = sorted(selected_benchmarks, key=lambda x: (x.split('_')[0], x.split('_')[1], x.split('_')[2]))
    print(sorted_selected_benchmarks)


# rename aflgo to aflgoexp for aflgoexp's fuzzing data
def rename_aflgoexp_log_files(log_path):
    for file_name in os.listdir(log_path):
        if file_name.startswith('aflgo_'):
            old_file_path = os.path.join(log_path, file_name)
            new_file_name = 'aflgoexp_' + file_name[6:]
            new_file_path = os.path.join(log_path, new_file_name)
            os.rename(old_file_path, new_file_path)
            print(f'Renamed {old_file_path} to {new_file_path}')


if __name__ == '__main__':
    # # select 50 random benchmarks
    # select_50_random_benchmarks()
    
    # current_working_dir = os.getcwd()
    # home_dir = current_working_dir.split('ContinuousFuzzBench')[0]
    # aflgoexp_log_path = os.path.join(home_dir, 'data/aflgoexp/log')
    # rename_aflgoexp_log_files(aflgoexp_log_path)
    pass
