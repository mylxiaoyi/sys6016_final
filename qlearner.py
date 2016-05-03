import random
import sklearn
import numpy as np
from neuralnet import NeuralNet

class Q_Learner():
	def __init__(self, actions, epsilon=0.1, alpha=0.2, gamma=0.9):
		self.q = {}

		self.epsilon = epsilon
		self.alpha = alpha
		self.gamma = gamma
		self.actions = actions

		self.nn = NeuralNet()

	def getNNInput(self, state, action):
		ret = np.ndarray(shape=(1,6))
		ret[0][0] = state[0]
		ret[0][1] = state[1]
		ret[0][2] = state[2]
		ret[0][3] = state[3]
		ret[0][4] = state[4]
		ret[0][5] = action

		return ret

	# def getNNExpectedResult(self, state, action):
	# 	qval =  self.q[(state, action)]
	# 	return qval

	def getQNN(self, state, action):
		return self.nn.predict(self.getNNInput(state, action))

	def getQ(self, state, action):
		return self.q.get((state, action), 0.0)

	def learnQ(self, state, action, reward, value):
		old_val = self.getQNN(state, action)
		# if old_val is None:
		# 	self.q[(state, action)] = reward
		# else:
		# 	self.q[(state, action)] = old_val + self.alpha * (value + old_val)

		expected_val = old_val + self.alpha * (value + old_val)
		print "expected q val: %s" % expected_val 
		print "value: %s" % value

		# print "q val: %s" % self.getNNExpectedResult(state, action)

		self.nn.fit(self.getNNInput(state, action), expected_val)

	def chooseAction(self, state):

		if random.random() < self.epsilon:
			action = random.choice(self.actions)
		else:
			q = [self.getQNN(state, a) for a in self.actions]
			maxQ = max(q)
			count = q.count(maxQ)
			if count > 1:
				best = [i for i in range(len(self.actions)) if q[i] == maxQ]
				i = random.choice(best)
			else:
				i = q.index(maxQ)

			action = self.actions[i]
		return action

	def learn(self, state1, action1, reward, state2):
		maxqnew = max([self.getQNN(state2, a) for a in self.actions])
		self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)