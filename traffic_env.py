import os

import gymnasium as gym
from sumolib import checkBinary
import traci
import traci.exceptions
import numpy as np
import subprocess

YELLOW_TIME = 3.0

class TrafficEnv(gym.Env):
    def __init__(self, show_gui=False, situation_name="", num_steps=1000, green_phase_indexes = []):
        # spremanje parametara
        self.num_steps = num_steps
        self.situation_name = situation_name
        self.sumoBinary = checkBinary('sumo-gui' if show_gui else 'sumo')
        self.green_phase_indexes = green_phase_indexes

        # inicijalizacija
        self._next_phase = green_phase_indexes[0]

        # inicijalizira action space i observation space
        self.action_space = gym.spaces.Discrete(len(green_phase_indexes))
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(4*2+2, ), dtype=np.float64)
    
    def _get_observation(self):
        # struktura: [waiting0, halting0, waiting1, halting1, ... , curr_phase, curr_phase_elapsed_time]
        observation = []
        for lane in self.controlled_lanes:
            observation.append(traci.lane.getWaitingTime(lane))
            observation.append(traci.lane.getLastStepHaltingNumber(lane))
        observation.append(traci.trafficlight.getPhase("I0"))
        observation.append(traci.trafficlight.getSpentDuration("I0"))
        return np.array(observation, dtype=np.float64)

    def _get_reward(self):
        waiting_time = 0
        halting_num = 0
        for lane in self.controlled_lanes:
            waiting_time += traci.lane.getWaitingTime(lane)
            halting_num += traci.lane.getLastStepHaltingNumber(lane)
        
        reward = -waiting_time-halting_num
        return reward
    
    def reset(self, *, seed = None, options = None):
        file_path = f"situations/{self.situation_name}/{self.situation_name}"
        if traci.isLoaded():
            traci.load(["-n", file_path + ".net.xml", "-r", file_path + ".rou.xml"])
        else:
            result = subprocess.run([
                "python", f"{os.environ['SUMO_HOME']}/tools/randomTrips.py",
                "-n", file_path + ".net.xml",
                "-o", file_path + ".rou.xml",
                "--random",
                "--period", "1.5",
                "--end", str(self.num_steps),
                "--validate"
            ], capture_output=True)
            traci.start([self.sumoBinary, "-n", file_path + ".net.xml", "-r", file_path + ".rou.xml", "--start"])

        self._steps_passed = 0
        self.controlled_lanes = sorted(set(traci.trafficlight.getControlledLanes("I0")))
        observation = self._get_observation()
        return observation, {}
    
    def step(self, action):
        curr_phase = traci.trafficlight.getPhase("I0")
        if curr_phase in self.green_phase_indexes:
            if self.green_phase_indexes[action]!=curr_phase:
                traci.trafficlight.setPhase("I0", traci.trafficlight.getPhase("I0") + 1)
                self._next_phase = self.green_phase_indexes[action]
        else:
            if traci.trafficlight.getSpentDuration("I0") >= YELLOW_TIME:
                traci.trafficlight.setPhase("I0", self._next_phase)

        traci.simulationStep()
        self._steps_passed+=1

        observation = self._get_observation()
        reward = self._get_reward()
        sim_finished = traci.simulation.getMinExpectedNumber() <= 0
        terminated = self._steps_passed >= self.num_steps or sim_finished
        # terminated = traci.simulation.getMinExpectedNumber() <= 0
        return observation, reward, terminated, False, {}
    
    def close(self):
        # zavrsava simulaciju
        try:
            traci.close() # zatvara ako je vec otvoreno
        except traci.exceptions.FatalTraCIError:
            pass # nije ni bilo otvoreno