from os import makedirs
import matplotlib.pyplot as plt

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import plot_results
from stable_baselines3.common import results_plotter

from traffic_env import TrafficEnv

TOTAL_TIMESTEPS = 200000

log_dir = "tmp/"
makedirs(log_dir, exist_ok=True)

env = TrafficEnv("intersection01", 1000, [0, 2])
env = Monitor(env, log_dir)

model = PPO("MlpPolicy", env, verbose=1, n_steps=2048, batch_size=64)
model.learn(total_timesteps=TOTAL_TIMESTEPS)

model.save("situations/intersection01/intersection01")
env.close()

plot_results([log_dir], TOTAL_TIMESTEPS, results_plotter.X_TIMESTEPS, "PPO")
plt.show()