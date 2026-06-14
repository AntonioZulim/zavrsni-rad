from os import listdir, mkdir, path
import matplotlib.pyplot as plt
import numpy as np

from stable_baselines3 import PPO
from traffic_env import TrafficEnv

GREEN_DURATION = 30

def rolling_mean(data, window):
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode='valid')

def test_dist(model, dist_num):
    results = []
    results_base = []

    for route_index in range(len(listdir(f"situations/intersection01/test/dist{dist_num:02}"))):
        env = TrafficEnv("intersection01", 1000, [0, 2], test_index=route_index, dist=dist_num, show_gui=False)
        model.set_env(env)

        # fiksna signalizacija na 30s
        obs, _ = env.reset()
        try:
            episode_res = []
            for i in range(1000):
                action = (i//GREEN_DURATION) % len(env.green_phase_indexes)
                obs, reward, done, terminated, info = env.step(action)
                episode_res.append(info)
            results_base.append(episode_res)
        except:
            print("SUMO closed earlier!")
        finally:
            env.close()

        # signalizacija upravljana podrzanim ucenjem
        obs, _ = env.reset()
        try:
            episode_res = []
            for i in range(1000):
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, terminated, info = env.step(action)
                episode_res.append(info)
            results.append(episode_res)
        except:
            print("SUMO closed earlier!")
        finally:
            env.close()
    
    return results, results_base

model = PPO.load("situations/intersection01/intersection01")

if not path.exists("./graphs"):
    mkdir("./graphs")

for i in range(len(listdir(f"situations/intersection01/test"))):
    results, results_base = test_dist(model, i)

    rewards = [[step["reward"] for step in ep] for ep in results]
    waiting = [[step["waiting_time"] for step in ep] for ep in results]
    halting = [[step["halting_num"] for step in ep] for ep in results]

    waiting_base = [[step["waiting_time"] for step in ep] for ep in results_base]
    halting_base = [[step["halting_num"] for step in ep] for ep in results_base]

    mean = np.mean(rewards, axis=0)
    std = np.std(rewards, axis=0)
    plt.clf()
    plt.plot(rolling_mean(mean, 50), label="PPO - srednja vrijednost")
    plt.fill_between(np.arange(len(mean)), mean-std, np.clip(mean+std, a_min=None, a_max=0), alpha=0.3, label="PPO - standardna devijacija")
    plt.xlabel("Korak simulacije")
    plt.ylabel("Nagrada")
    plt.legend()
    plt.savefig(f"./graphs/test_rewards_dist{i:02}.png", format="png")

    mean = np.mean(waiting, axis=0)
    std = np.std(waiting, axis=0)
    mean_base = np.mean(waiting_base, axis=0)
    plt.clf()
    plt.plot(rolling_mean(mean, 50), label="PPO - srednja vrijednost")
    plt.fill_between(np.arange(len(mean)), np.clip(mean-std, a_min=0, a_max=None), mean+std, alpha=0.3, label="PPO - standardna devijacija")
    plt.plot(rolling_mean(mean_base, 50), label="Fiksni intervali - srednja vrijednost")
    plt.xlabel("Korak simulacije")
    plt.ylabel("Ukupno vrijeme čekanja po koraku (s)")
    plt.legend()
    plt.savefig(f"./graphs/test_waiting_dist{i:02}.png", format="png")

    mean = np.mean(halting, axis=0)
    std = np.std(halting, axis=0)
    mean_base = np.mean(halting_base, axis=0)
    plt.clf()
    plt.plot(rolling_mean(mean, 50), label="PPO - srednja vrijednost")
    plt.fill_between(np.arange(len(mean)), np.clip(mean-std, a_min=0, a_max=None), mean+std, alpha=0.3, label="PPO - standardna devijacija")
    plt.plot(rolling_mean(mean_base, 50), label="Fiksni intervali - srednja vrijednost")
    plt.xlabel("Korak simulacije")
    plt.ylabel("Broj zaustavljenih vozila")
    plt.legend()
    plt.savefig(f"./graphs/test_halting_dist{i:02}.png", format="png")