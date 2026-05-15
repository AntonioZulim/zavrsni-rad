import gymnasium as gym
from stable_baselines3 import PPO
from traffic_env import TrafficEnv

env = TrafficEnv(True, "intersection01", 100, [0, 2])
model = PPO("MlpPolicy", env, verbose=1, n_steps=100, batch_size=100)
model.load("situations/intersection01/intersection01")

vec_env = model.get_env()
obs = vec_env.reset()
for i in range(100):
    action, _state = model.predict(obs, deterministic=True)
    obs, reward, done, info = vec_env.step(action)