import sys
from pygame.math import Vector2
from qlearner import Q_Learner
from geometry import calculateIntersectPoint
import math
import random


responses = 3

class Car():
	def __init__(self, position, velocity, turnRadius):

		self.init_position = Vector2(position)
		self.init_velocity = Vector2(velocity)

		self.position = Vector2(position)
		self.velocity = Vector2(velocity)
		self.turnRadius = turnRadius
		
		self.sensor_length = 100
		self.base_sensor = velocity.normalize()*self.sensor_length
		self.sensors = [self.base_sensor, 
						self.base_sensor.rotate(-20),
						self.base_sensor.rotate(-40),
						self.base_sensor.rotate(20),
						self.base_sensor.rotate(40)]

		self.ai = Q_Learner(actions = range(responses),  alpha=0.1, gamma=0.9, epsilon=0.1)
		self.crashes = 0
		self.best_time = 0

		self.lastState = None
		self.lastAction = None

	def reset(self):
		self.position = Vector2(self.init_position)
		print "init position:" + str(self.init_position)
		self.velocity = Vector2(self.init_velocity)
		self.sensors = [self.base_sensor, 
						self.base_sensor.rotate(-20),
						self.base_sensor.rotate(-40),
						self.base_sensor.rotate(20),
						self.base_sensor.rotate(40)]

	def out_of_bounds(self, (window_width, window_height)):
	    position = self.get_position()
	    if position[0] < 0 or position[1] < 0 or position[0] >= window_width or position[1] >= window_height:
	        return True
	    return False

	def collision(self, obstacles):
	    cp = self.get_position()
	    for o in obstacles:
	        if cp[0] >= o.p1[0] and cp[0] >= o.p4[0] and cp[0] <= o.p2[0] and cp[0] <= o.p3[0] and cp[1] >= o.p1[1] and cp[1] >= o.p2[1] and cp[1] <= o.p3[1] and cp[1] <= o.p4[1]:
	            return True
	    return False

	def compute_dist(self, p1, p2):
		return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) 


	def calc_state(self, sensor_data):
		s_data = []

		s_data.append(int(sensor_data[0]["dist"]))
		s_data.append(int(sensor_data[1]["dist"]))
		s_data.append(int(sensor_data[2]["dist"]))
		s_data.append(int(sensor_data[3]["dist"]))
		s_data.append(int(sensor_data[4]["dist"]))

		for i in range(len(s_data)):
			if s_data[i] > self.sensor_length:
				s_data[i] = 0
			elif s_data[i] < 10:
				s_data[i] = 1
			elif s_data[i] < 20:
				s_data[i] = 2
			elif s_data[i] < 30:
				s_data[i] = 3
			elif s_data[i] < 40:
				s_data[i] = 4
			elif s_data[i] < 50:
				s_data[i] = 5
			elif s_data[i] < 60:
				s_data[i] = 6
			elif s_data[i] < 70:
				s_data[i] = 7
			elif s_data[i] < 80:
				s_data[i] = 8
			elif s_data[i] < 90:
				s_data[i] = 9
			else:
				s_data[i] = 10

		return (s_data[0], s_data[1], s_data[2], s_data[3], s_data[4])

	def check_sensors(self, obstacles):
	    max_float = sys.float_info.max


	    sensor_lines = self.get_sensor_lines()
	    sensor_hits = {0: {"dist": max_float, "point": None}, 1: {"dist": max_float, "point": None}, 2:  {"dist": max_float, "point": None}, 3:  {"dist": max_float, "point": None}, 4:  {"dist": max_float, "point": None}}
	    for o in obstacles:
	        for i in range(len(sensor_lines)):
	            s_line = sensor_lines[i]
	            o_lines = o.get_lines()
	            for o_line in o_lines:
	                p  = calculateIntersectPoint(s_line[0], s_line[1], o_line[0], o_line[1])
	                if p:
	                    dist = self.compute_dist(self.get_position(), p)
	                    if dist < sensor_hits[i]["dist"]: 
	                        sensor_hits[i]["dist"] = dist
	                        sensor_hits[i]["point"] = p
	    return sensor_hits

	def update(self, obstacles, window_bounds):

		sensor_data = self.check_sensors(obstacles)
		state = self.calc_state(sensor_data)
		action = self.ai.chooseAction(state)
		print "%s: %s" %  (state, action)

		if action == 0:
			self.turn_left()
		elif action == 1:
			self.turn_right()
		self.update_position()

		did_reset = False

		if self.out_of_bounds(window_bounds) or self.collision(obstacles):
			self.crashes += 1
			reward = -100
			if self.lastState is not None:
				self.ai.learn(self.lastState, self.lastAction, reward, state)
			self.lastState = None
			self.lastAction = None

			self.reset()

			did_reset = True
		else:
			reward = 0
			if self.lastState is not None:
				self.ai.learn(self.lastState, self.lastAction, reward, state)


		self.lastState = state
		self.lastAction = action



		return (sensor_data, did_reset)


	def update_sensor_angle(self, angle):
		for i in range(len(self.sensors)):
			self.sensors[i] = self.sensors[i].rotate(angle)

	def turn_left(self):
		self.velocity = self.velocity.rotate(-self.turnRadius)
		self.update_sensor_angle(-self.turnRadius)

	def turn_right(self):
		self.velocity = self.velocity.rotate(self.turnRadius)
		self.update_sensor_angle(self.turnRadius)

	def get_position(self):
		return (int(self.position.x), int(self.position.y))

	def get_sensor_endpoint(self, i):
		return (int(self.position.x + self.sensors[i].x), int(self.position.y + self.sensors[i].y))

	def get_sensor_lines(self):
		return [(self.position, self.position + self.sensors[0]),
				(self.position, self.position + self.sensors[1]),
				(self.position, self.position + self.sensors[2]),
				(self.position, self.position + self.sensors[3]),
				(self.position, self.position + self.sensors[4])]

	def update_sensor_positions(self):
		for i in range(len(self.sensors)):
			self.sensors[i].x = self.sensors[i].x + self.velocity.x
			self.sensors[i].y = self.sensors[i].y + self.velocity.y

	def update_position(self):
		self.position.x  = self.position.x + self.velocity.x
		self.position.y = self.position.y + self.velocity.y


