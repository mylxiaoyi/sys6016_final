#q learning code  
#from https://github.com/studywolf/blog/tree/master/RL/Cat%20vs%20Mouse%20exploration

import random

class BaseQLearn:
    def __init__(self, actions, epsilon=0.1, alpha=0.2, gamma=0.9):
        self.q = {}

        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions

    def getQ(self, state, action):
        """
        Get relevant q value from table
        """
        return self.q.get((state, action), 0.0)
        # return self.q.get((state, action), 1.0)

    def learnQ(self, state, action, reward, value):
        """
        Update q table based on reward function
        """
        oldv = self.q.get((state, action), None)
        if oldv is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = oldv + self.alpha * (value - oldv)

    def chooseAction(self, state):
        """
        Select action based on current state
        """

        #epsilon may cause random choice
        if random.random() < self.epsilon:
            action = random.choice(self.actions)

        #select best q value, given state
        else:
            q = [self.getQ(state, a) for a in self.actions]
            maxQ = max(q)
            count = q.count(maxQ)
            # if tie, select randomly
            if count > 1:
                best = [i for i in range(len(self.actions)) if q[i] == maxQ]
                i = random.choice(best)
            else:
                i = q.index(maxQ)

            #return action associated with q value
            action = self.actions[i]
        return action

    def learn(self, state1, action1, reward, state2):
        #find best action for new state
        maxqnew = max([self.getQ(state2, a) for a in self.actions])
        #run learnq with updated reward from taking best action in new state
        self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)

import math
def ff(f,n):
    fs = "{:f}".format(f)
    if len(fs) < n:
        return ("{:"+n+"s}").format(fs)
    else:
        return fs[:n]