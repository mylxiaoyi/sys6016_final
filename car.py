import sys
from pygame.math import Vector2
from qlearner import Q_Learner
from baseqlearner import BaseQLearn
from qlearnermodrandom import RandQLearn
from geometry import calculateIntersectPoint
import math
import random
import datetime
import json
import os
from ast import literal_eval
from qnn import QNN

#############
# Constants #
#############
RESPONSES = 3
REWARD_CRASH = -100
REWARD_SENSOR = -1
REWARD_CLEAR = 10

class Car():
	"""
	Car class
	"""

	def __init__(self, car_params):

		# Save initial position and velocity for reset on crash
		self.init_position = Vector2(car_params["position"])
		self.init_velocity = Vector2(car_params["velocity"])

		# Set (dynamic) initial position and velocity
		self.position = Vector2(car_params["position"])
		self.velocity = Vector2(car_params["velocity"])

		# Set turn radius
		self.turnRadius = car_params["turn_radius"]
		
		# Set base sensor length
		self.sensor_length = car_params["sensor_length"]

		# Create endpoints for sensors
		self.base_sensor = self.velocity.normalize()*self.sensor_length
		self.sensors = [self.base_sensor, 
						self.base_sensor.rotate(-20),
						self.base_sensor.rotate(-40),
						self.base_sensor.rotate(20),
						self.base_sensor.rotate(40)]

		# Set machine learning algorithm to be used by car to explore space
		# self.ai = RandQLearn(actions = range(RESPONSES),  alpha=0.1, gamma=0.9, epsilon=0.1)
		self.ai = QNN()

		# Initialize variables which contain relevant car data
		self.crashes = 0
		self.best_time = 0

		# Fields used by q-learning algorithm
		self.lastState = None
		self.lastAction = None

		# Boolean indicating whether to save state or not
		self.log_state = car_params["log_state"]

		# Load a previously saved state, if one is provided
		if car_params["load_state_path"] is not None:
			self.load_state(car_params["load_state_path"])

	def reset(self):
		"""
		Reset car position and velocity on crash
		"""
		print "Crash! Resetting."
		self.position = Vector2(self.init_position)
		self.velocity = Vector2(self.init_velocity)
		self.sensors = [self.base_sensor, 
						self.base_sensor.rotate(-20),
						self.base_sensor.rotate(-40),
						self.base_sensor.rotate(20),
						self.base_sensor.rotate(40)]

	def out_of_bounds(self, (window_width, window_height)):
		"""
		Determine whether car has hit edges of screen or not
		"""
		position = self.get_position()
		if position[0] < 0 or position[1] < 0 or position[0] >= window_width or position[1] >= window_height:
			return True
		return False

	def collision(self, obstacles):
		"""
		Determine whether car has hit an obstacle
		"""
		cp = self.get_position()
		for o in obstacles:
			if cp[0] >= o.p1[0] and cp[0] >= o.p4[0] and cp[0] <= o.p2[0] and cp[0] <= o.p3[0] and cp[1] >= o.p1[1] and cp[1] >= o.p2[1] and cp[1] <= o.p3[1] and cp[1] <= o.p4[1]:
				return True
		return False

	def compute_dist(self, p1, p2):
		"""
		Helper method to compute the distance between two points
		"""
		return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) 


	def calc_state(self, sensor_data):
		"""
		Convert sensor data into tractable state tuple
		"""

		s_data = []

		s_data.append(int(sensor_data[0]["dist"]))
		s_data.append(int(sensor_data[1]["dist"]))
		s_data.append(int(sensor_data[2]["dist"]))
		s_data.append(int(sensor_data[3]["dist"]))
		s_data.append(int(sensor_data[4]["dist"]))

		for i in range(len(s_data)):
			s_data[i] = int(s_data[i] / 20)	
			if s_data[i] > 10:
				s_data[i] = 11

		return (s_data[0], s_data[1], s_data[2], s_data[3], s_data[4])

	def check_sensors(self, obstacles, window_bounds):
		"""
		Check to see if sensors have hit anything
		"""

		max_float = sys.float_info.max
		sensor_lines = self.get_sensor_lines()

		#Object to keep track of distance and location of any sensor hits
		sensor_hits = {0: {"dist": max_float, "point": None}, 
						1: {"dist": max_float, "point": None}, 
						2:  {"dist": max_float, "point": None}, 
						3:  {"dist": max_float, "point": None}, 
						4:  {"dist": max_float, "point": None}}

		# check for collisions
		for i in range(len(sensor_lines)):

			s_line = sensor_lines[i]

			# SCREEN BOUNDARIES

			w_0 = (0, 0)
			w_1 = (window_bounds[0],0)
			w_2 = (0, window_bounds[1])
			w_3 = (window_bounds[0], window_bounds[1])

			w_lines = []
			w_lines.append((w_0, w_1))
			w_lines.append((w_1, w_3))
			w_lines.append((w_3, w_2))
			w_lines.append((w_2, w_0))

			for wall in w_lines:
				p  = calculateIntersectPoint(s_line[0], s_line[1], wall[0], wall[1])
				if p:
					dist = self.compute_dist(self.get_position(), p)
					if dist < sensor_hits[i]["dist"] and dist < self.sensor_length: 
						sensor_hits[i]["dist"] = dist
						sensor_hits[i]["point"] = p
			# OBSTACLES

			for o in obstacles:
				o_lines = o.get_lines()
				for o_line in o_lines:
					p  = calculateIntersectPoint(s_line[0], s_line[1], o_line[0], o_line[1])
					if p:
						dist = self.compute_dist(self.get_position(), p)
						if dist < sensor_hits[i]["dist"] and dist < self.sensor_length: 
							sensor_hits[i]["dist"] = dist
							sensor_hits[i]["point"] = p
		return sensor_hits

	def update(self, obstacles, window_bounds):
		"""
		Update car position
		"""

		# Collect sensor data
		sensor_data = self.check_sensors(obstacles, window_bounds)
		# Convert sensor data into state
		state = self.calc_state(sensor_data)
		# Use AI system to decide action to take
		action = self.ai.chooseAction(state)

		# Take decided action
		if action == 0:
			self.turn_left()
		elif action == 1:
			self.turn_right()
		self.update_position()

		# TRAIN CLASSIFIER

		did_reset = False

		# If crashed, provide very large negative reward
		if self.out_of_bounds(window_bounds) or self.collision(obstacles):
			self.crashes += 1
			if self.lastState is not None:
				self.ai.learn(self.lastState, self.lastAction, REWARD_CRASH, self.calc_state(sensor_data))
			self.lastState = None
			self.lastAction = None

			self.reset()

			did_reset = True

			if self.log_state and self.crashes % 1000 == 0 and self.crashes != 0:
				self.save_state()

		# If sensors are not triggering (in open space), provide large positive reward
		elif sensor_data[0]["dist"] == 0 and sensor_data[1]["dist"] == 0 and sensor_data[2]["dist"] == 0 and sensor_data[3]["dist"] == 0 and sensor_data[4]["dist"] == 0:
			if self.lastState is not None:
				self.ai.learn(self.lastState, self.lastAction, REWARD_CLEAR, state)	

		# Otherwise, provide very small reward (want to stay away from all "crashable" regions 
		# as much as possible)
		else:
			if self.lastState is not None:
				self.ai.learn(self.lastState, self.lastAction, REWARD_SENSOR, state)

		# Update stored last state and action taken
		self.lastState = state
		self.lastAction = action

		return (sensor_data, did_reset)


	def update_sensor_angle(self, angle):
		"""
		Helper method to update sensor endpoint locations
		"""

		for i in range(len(self.sensors)):
			self.sensors[i] = self.sensors[i].rotate(angle)

	def turn_left(self):
		"""
		Update car velocity and sensor endpoints (left turn)
		"""
		self.velocity = self.velocity.rotate(-self.turnRadius)
		self.update_sensor_angle(-self.turnRadius)

	def turn_right(self):
		"""
		Update car velocity and sensor endpoints (right turn)
		"""
		self.velocity = self.velocity.rotate(self.turnRadius)
		self.update_sensor_angle(self.turnRadius)

	def get_position(self):
		"""
		Get current car position
		"""
		return (int(self.position.x), int(self.position.y))

	def get_sensor_endpoint(self, i):
		"""
		Get ith sensor endpoint
		"""
		return (int(self.position.x + self.sensors[i].x), int(self.position.y + self.sensors[i].y))

	def get_sensor_lines(self):
		"""
		Get tuples of points indicating lines to be drawn on screen
		"""
		return [(self.position, self.position + self.sensors[0]),
				(self.position, self.position + self.sensors[1]),
				(self.position, self.position + self.sensors[2]),
				(self.position, self.position + self.sensors[3]),
				(self.position, self.position + self.sensors[4])]

	def update_sensor_positions(self):
		"""
		Update the positions of the sensor endpoints based on car velocity
		"""
		for i in range(len(self.sensors)):
			self.sensors[i].x = self.sensors[i].x + self.velocity.x
			self.sensors[i].y = self.sensors[i].y + self.velocity.y

	def update_position(self):
		"""
		Update car position based on car velocity
		"""
		self.position.x  = self.position.x + self.velocity.x
		self.position.y = self.position.y + self.velocity.y

	def save_state(self):
		"""
		Optional state save of classifier to mitigate unnecessary retraining
		Save as json object
		"""
		print "saving state."
		fname = os.path.join("models", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
		tmp_q = {}
		for key in self.ai.q:
			tmp_q[str(key)] = self.ai.q[key]

		with open(fname, "w") as f:
			json.dump(tmp_q, f)

	def load_state(self, fname):
		"""
		Load json object representing classifier
		"""
		print "loading state."
		with open(fname, "r") as f:
			tmp_q = json.load(f)
			for key in tmp_q:
				self.ai.q[literal_eval(key)] = tmp_q[key]


