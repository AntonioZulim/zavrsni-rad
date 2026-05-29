import os
import numpy as np

from stable_baselines3 import PPO
from traffic_env import TrafficEnv

GREEN_DURATION = 30

model = PPO.load("situations/intersection01/intersection01")
results_base = []
results_rl = []

for route_index in range(len(os.listdir(f"situations/intersection01/test"))):
    env = TrafficEnv("intersection01", 1000, [0, 2], test_index=route_index, show_gui=False)
    model.set_env(env)

    obs, _ = env.reset()
    for i in range(1000):
        action = (i//GREEN_DURATION) % len(env.green_phase_indexes)
        obs, reward, done, terminated, info = env.step(action)
    results_base.append(info)

    obs, _ = env.reset()
    try:
        for i in range(1000):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, terminated, info = env.step(action)
        results_rl.append(info)
    except:
        print("SUMO closed earlier!")
    finally:
        env.close()

print(f"BASE avg waiting: {np.mean([el["total_waiting"] for el in results_base])}")
print(f"BASE avg halting: {np.mean([el["total_halting"] for el in results_base])}")
print(f"RL avg waiting: {np.mean([el["total_waiting"] for el in results_rl])}")
print(f"RL avg halting: {np.mean([el["total_halting"] for el in results_rl])}")


