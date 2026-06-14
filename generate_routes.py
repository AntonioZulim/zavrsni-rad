import os
import shutil
import subprocess
import random

rates = [
    500, # slabi promet
    1000, # normalni promet
    2000, # povecani promet
    [800, 1200, 600],
    [1600, 2250, 1800]
]

def clear_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def split_counts(routes_num, categories_num):
    q = routes_num//categories_num
    r = routes_num%categories_num
    return [q+1] * r + [q] * (categories_num-r)

def generate_route(file_path, situation, num_steps, insertion_rate):
    rate_list = [str(insertion_rate)] if isinstance(insertion_rate, int) else [str(el) for el in insertion_rate]
    return subprocess.run([
        "python", f"{os.environ['SUMO_HOME']}/tools/randomTrips.py",
        "-n", f"situations/{situation}/{situation}.net.xml",
        "-o", file_path + ".rou.xml",
        "--random",
        "--insertion-rate"
    ] + rate_list + [
        "--end", str(num_steps),
        "--validate"
    ], capture_output=True)

def generate_routes(situation, num_steps, num_routes):
    num_train_routes = int(num_routes * 0.7)

    clear_folder(f"situations/{situation}/train")
    for i in range(num_train_routes):
        generate_route(f"situations/{situation}/train/route{i:03}", situation, num_steps, random.choice(rates))
        print(str(i) + " train files done")
    
    clear_folder(f"situations/{situation}/test")
    counts_list = split_counts(num_routes-num_train_routes, len(rates))
    for i in range(len(counts_list)):
        os.mkdir(f"situations/{situation}/test/dist{i:02}")
        for j in range(counts_list[i]):
            generate_route(f"situations/{situation}/test/dist{i:02}/route{j:03}", situation, num_steps, rates[i])
            print(f"{j} dist{i:02} test files done")

generate_routes("intersection01", 1000, 200)