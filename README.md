# Reinforcement Learning for Traffic Light Control

Implementation of the bachelor's thesis **"Applying Reinforcement Learning for Traffic Light Control at Intersections"**.

The project uses **Proximal Policy Optimization (PPO)** to control traffic lights in a simulated intersection. Traffic is simulated using **Eclipse SUMO**, with **Gymnasium** and **Stable-Baselines3** used for the reinforcement learning environment and PPO implementation.

## Project Structure

- `traffic_env.py` — Gymnasium environment for traffic light control
- `train.py` — trains the PPO agent
- `run.py` — evaluates the trained agent and compares it with fixed-time traffic lights
- `generate_routes.py` — generates training and testing traffic scenarios
- `situations/` — traffic scenarios, routes and trained models
- `graphs/` — generated training and evaluation graphs

## Usage

### Generate traffic scenarios

    python generate_routes.py

This generates **200 scenarios**: 140 for training and 60 for testing, across five traffic intensity categories.

### Train the model

    python train.py

The PPO agent is trained for **200,000 timesteps** and the trained model is saved under `situations/intersection01/`.

### Evaluate the model

    python run.py

The evaluation compares the PPO controller with a fixed-time traffic light controller using **30-second phase durations**. Results are saved in `graphs/`.

## Results

At high traffic intensity, the trained PPO controller achieved less than half of the accumulated vehicle waiting time compared to the fixed-phase system. At low and medium traffic intensities, the PPO controller performed comparably to the fixed-phase system.

## Requirements

- Python 3.x
- Eclipse SUMO
- Gymnasium
- Stable-Baselines3
- NumPy
- Matplotlib
