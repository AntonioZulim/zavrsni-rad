import os
import shutil
import subprocess
import random

def clear_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def generate_route(file_path, situation, num_steps, insertion_rate):
    return subprocess.run([
        "python", f"{os.environ['SUMO_HOME']}/tools/randomTrips.py",
        "-n", f"situations/{situation}/{situation}.net.xml",
        "-o", file_path + ".rou.xml",
        "--random",
        "--insertion-rate", str(insertion_rate),
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
    for i in range(num_routes-num_train_routes):
        generate_route(f"situations/{situation}/test/route{i:03}", situation, num_steps)
        print(str(i) + " test files done")

generate_routes("intersection01", 1000, 100)