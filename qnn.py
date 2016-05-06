
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
import random
import numpy as np

#############
# CONSTANTS #
#############
GAMMA = 0.9
EPSILON = 1

class QNN:

	def __init__(self):
		self.model = Sequential()
		self.model.add(Dense(164, init='lecun_uniform', input_shape=(5,)))
		self.model.add(Activation('relu'))

		self.model.add(Dense(150, init='lecun_uniform'))
		self.model.add(Activation('relu'))

		self.model.add(Dense(3, init='lecun_uniform'))
		self.model.add(Activation('linear'))

		self.rms = RMSprop()
		self.model.compile(loss='mse', optimizer=self.rms)

		print self.model.predict(np.zeros((1, 5)), batch_size=1)

		self.gamma = 0.9
		self.epsilon = 1

		self.qval = np.zeros((1,3))


	def chooseAction(self, state):
		state = np.asarray(state)
		print state.shape
		print "choosing action"
		print state.reshape(1, 5)
		self.qval = self.model.predict(state.reshape((1, 5)), batch_size=1)
		print self.qval
		if random.random() < self.epsilon:
			action = np.random.randint(0, 3)
		else:
			action = (np.argmax(qval))
		self.action = action
		return action


	def learn(self, last_state, last_action, reward, new_state):

		new_state = np.asarray(new_state)
		last_state = np.asarray(last_state)
		last_action = np.asarray(last_action)

		newQ = self.model.predict(new_state.reshape((1, 5)), batch_size=1)
		maxQ = np.max(newQ)
		y = np.zeros((1,3))
		y[:] = self.qval[:]
		if reward != -100:
			update = (reward + (self.gamma * maxQ))
		else:
			update = reward
		y[0][self.action] = update
		self.model.fit(last_state.reshape(1,5), y, batch_size=1, nb_epoch=1, verbose=1)

		if self.epsilon > 0.1:
			self.epsilon -= (1/10000)


