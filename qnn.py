from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
import random
import numpy as np

class QNN:
	"""
	This class is our implementation of a Q-Table approximation using a neural network.
	We make use of the keras library to create and run the neural net (http://keras.io/).

	From http://outlace.com/Reinforcement-Learning-Part-3/

	This module runs in two modes, where experience_replay can be turned on/off.

	"""

	def __init__(self):

		#set to counteract catastrophic forgetting
		self.experience_replay = True

		#initialize base parameters
		self.crash_reward = -100
		self.input_size = 5
		self.output_size = 3

		#build neural net, modifying hidden layers as necessary
		self.model = Sequential()
		self.model.add(Dense(30, init='lecun_uniform', input_shape=(self.input_size,)))
		self.model.add(Activation('relu'))

		self.model.add(Dense(20, init='lecun_uniform'))
		self.model.add(Activation('relu'))

		self.model.add(Dense(3, init='lecun_uniform'))
		self.model.add(Activation('linear'))

		self.rms = RMSprop()
		self.model.compile(loss='mse', optimizer=self.rms)

		#set base gamma and epsilon
		self.gamma = 0.9
		self.epsilon = 1.0

		self.qval = np.zeros((1,self.output_size))

		#initialize experience replay fields
		self.replay = []
		self.buffer=80
		self.batchSize = 20
		self.h = 0

	def convert_state_action_tuple(self, state, action):
		"""
		Helper method for converting state/action into a large tuple (not used in current implementation)
		"""
		return (state[0], state[1], state[2], state[3], state[4], action)

	def create_input_data(self, state):
		"""
		Convert input tuple into numpy array
		"""
		return np.asarray(state)

	def chooseAction(self, state):
		"""
		Select action based on state
		"""
		
		#format input data
		in_data = self.create_input_data(state)

		#predict on input data
		self.qval = self.model.predict(in_data.reshape((1, self.input_size)), batch_size=1)

		#potentially select a random decision, based on epsilon
		#otherwise, select the maximum qval from the output
		if random.random() < self.epsilon:
			action = np.random.randint(0, self.output_size)
		else:
			action = (np.argmax(self.qval))
		#update currently selected action
		self.action = action
		return action


	def learn(self, last_state, last_action, reward, new_state):

		#if running experience replay
		if self.experience_replay:

			#save current state to replay buffer, overwriting old values
			#as necessary
			replay_tup = (last_state, last_action, reward, new_state)
			if len(self.replay) < self.buffer:
				self.replay.append(replay_tup)
			#if buffer is full:
			else:
				if self.h < self.buffer-1:
					self.h += 1
				else:
					self.h = 0
				self.replay[self.h] = replay_tup

				#select random subset from buffer
				minibatch = random.sample(self.replay, self.batchSize)

				#train on random subset
				X_train = []
				y_train = []

				for memory in minibatch:
					#Get max_Q(S',a)
					(last_s, last_a, rew, new_s) = memory
					last_s = np.asarray(last_s)
					new_s = np.asarray(new_s)
					old_qval = self.model.predict(last_s.reshape(1,self.input_size), batch_size=1)
					newQ = self.model.predict(new_s.reshape(1,self.input_size), batch_size=1)
					maxQ = np.max(newQ)

					#append to minibatch
					y = np.zeros((1,self.output_size))
					y[:] = old_qval[:]
					if reward != self.crash_reward: #non-terminal state
					    update = (reward + (self.gamma * maxQ))
					else: #terminal state
					    update = reward
					y[0][self.action] = update
					X_train.append(last_s.reshape(self.input_size,))
					y_train.append(y.reshape(self.output_size,))

				X_train = np.array(X_train)
				y_train = np.array(y_train)

				#fit to minibatch
				self.model.fit(X_train, y_train, batch_size=self.batchSize, nb_epoch=1, verbose=0)


		# if not running experience replay
		else:
			#format input data
			last_in = self.create_input_data(last_state)
			new_in =  self.create_input_data(new_state)

			#predict on input data, select max
			newQ = self.model.predict(new_in.reshape((1, self.input_size)), batch_size=1)
			maxQ = np.max(newQ)

			#update relevant reward in output array
			y = np.zeros((1,self.output_size))
			y[:] = self.qval[:]
			if reward != self.crash_reward: #if not in crash state:
				update = (reward + (self.gamma * maxQ))
			else:
				update = reward

			#backprop on updated output
			y[0][self.action] = update
			self.model.fit(last_in.reshape(1,self.input_size), y, batch_size=1, nb_epoch=1, verbose=1)



