import numpy as np

class NeuralNet():


	def __init__(self):
		self.nn_input_dim = 6
		self.nn_output_dim = 1
		self.epsilon = 1.0 # learning rate for gradient descent
		self.reg_lambda = 0.01 # regularization strength

		self.syn0 = self.randomize((6, 10))
		self.syn1 = self.randomize((10, 20))
		self.syn2 = self.randomize((20, 10))
		self.syn3 = self.randomize((10, 1))

		self.l0 = self.randomize((1, 6))
		self.l1 = self.nonlin(np.dot(self.l0,self.syn0))
		self.l2 = self.nonlin(np.dot(self.l1,self.syn1))
		self.l3 = self.nonlin(np.dot(self.l2,self.syn2))
		self.l4 = self.nonlin(np.dot(self.l3,self.syn3))


	def randomize(self, size):
		return 2*np.random.random(size) - 1

	def predict(self, state):
		self.l0 = state
		self.l1 = self.nonlin(np.dot(self.l0,self.syn0))
		self.l2 = self.nonlin(np.dot(self.l1,self.syn1))
		self.l3 = self.nonlin(np.dot(self.l2,self.syn2))
		self.l4 = self.nonlin(np.dot(self.l3,self.syn3))
		return self.l4[0]

	def fit(self, state, expected_q):
		predicted_q = self.predict(state)

		l4_error = expected_q - predicted_q
		print "error: %s" % (l4_error) 
		l4_delta = l4_error * self.nonlin(self.l4,deriv=True)

		l3_error = l4_delta.dot(self.syn3.T)
		l3_delta = l3_error * self.nonlin(self.l3,deriv=True)

		l2_error = l3_delta.dot(self.syn2.T)
		l2_delta = l2_error * self.nonlin(self.l2,deriv=True)

		l1_error = l2_delta.dot(self.syn1.T)
		l1_delta = l1_error * self.nonlin(self.l1,deriv=True)

		self.syn3 += self.epsilon * self.l3.T.dot(l4_delta)
		self.syn2 += self.epsilon * self.l2.T.dot(l3_delta)
		self.syn1 += self.epsilon * self.l1.T.dot(l2_delta)
		self.syn0 += self.epsilon * self.l0.T.dot(l1_delta)

	# sigmoid function
	def nonlin(self, x,deriv=False):
		if(deriv==True):
			return x*(1-x)
		return 1/(1+np.exp(-x))



if __name__ == "__main__":
	print "running neural net tests..."
	nn = NeuralNet()

	state = np.array([[5,5,5,5,5,1]])

	print nn.predict(state)
	nn.fit(state, 0)
	nn.fit(state, 0)
	nn.fit(state, 0)
	nn.fit(state, 0)
	nn.fit(state, 0)
	nn.fit(state, 0)
	nn.fit(state, 0)
	print nn.predict(state)