import gymnasium as gym
from sumolib import checkBinary
import traci
import traci.exceptions
import numpy as np
import os

YELLOW_TIME = 3.0
MIN_GREEN_TIME = 10.0

class TrafficEnv(gym.Env):
    def __init__(self, situation_name="", num_steps=1000, green_phase_indexes=[], test_index=-1, show_gui=False):
        # spremanje parametara
        self.num_steps = num_steps
        self.situation_name = situation_name
        self.sumoBinary = checkBinary('sumo-gui' if show_gui else 'sumo')
        self.green_phase_indexes = green_phase_indexes
        self.test_index = test_index

        # inicijalizacija
        self._next_phase = green_phase_indexes[0]
        self.train_num = len(os.listdir(f"situations/{self.situation_name}/train"))

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
        
        # pohrani metriku
        self.total_waiting += waiting_time
        self.total_halting += halting_num
        
        reward = - waiting_time/1000.0 - (halting_num ** 2/100.0)
        return reward
    
    def reset(self, *, seed = None, options = None):
        file_path = f"situations/{self.situation_name}/{self.situation_name}" # putanja za net datoteku
        # putanja za route datoteku
        if self.test_index==-1:
            rand = np.random.randint(0, self.train_num)
            route_file = f"situations/{self.situation_name}/train/route{rand:03}"
        else:
            route_file = f"situations/{self.situation_name}/test/route{self.test_index:03}"
        
        # ucitavanje simulacije
        if traci.isLoaded():
            traci.load(["-n", file_path + ".net.xml", "-r", route_file + ".rou.xml"])
        else:
            traci.start([self.sumoBinary, "-n", file_path + ".net.xml", "-r", route_file + ".rou.xml"])

        # inicijalizacija
        self.total_waiting = 0
        self.total_halting = 0
        self._steps_passed = 0
        self.controlled_lanes = sorted(set(traci.trafficlight.getControlledLanes("I0")))
        observation = self._get_observation()
        info = {
            "total_waiting": self.total_waiting,
            "total_halting": self.total_halting
        }
        return observation, info
    
    def step(self, action):
        # izracunaj sljedeci korak
        curr_phase = traci.trafficlight.getPhase("I0")
        passed_time = traci.trafficlight.getSpentDuration("I0")
        if curr_phase in self.green_phase_indexes:
            if self.green_phase_indexes[action]!=curr_phase and passed_time>=MIN_GREEN_TIME:
                traci.trafficlight.setPhase("I0", traci.trafficlight.getPhase("I0") + 1)
                self._next_phase = self.green_phase_indexes[action]
        else:
            if passed_time >= YELLOW_TIME:
                traci.trafficlight.setPhase("I0", self._next_phase)

        # izvedi korak u simulaciji
        traci.simulationStep()
        self._steps_passed+=1

        # izracun povratnih vrijednosti
        observation = self._get_observation()
        reward = self._get_reward()
        sim_finished = traci.simulation.getMinExpectedNumber() <= 0
        terminated = self._steps_passed >= self.num_steps or sim_finished
        info = {
            "total_waiting": self.total_waiting,
            "total_halting": self.total_halting
        }
        return observation, reward, terminated, False, info
    
    def close(self):
        # zavrsava simulaciju
        try:
            traci.close() # zatvara ako je vec otvoreno
        except traci.exceptions.FatalTraCIError:
            pass # nije ni bilo otvoreno