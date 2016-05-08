# sys6016_final

## Zack Verham, Taylor Mcnally, Jianyu Su, Constance Hu

### Description

This is our team's final project for SYS6016 (Machine Learning). 

For our project, we built a 2-D model of a self-taught autonomous car which improves itself through a reinforcement method called [Q-Learning](https://en.wikipedia.org/wiki/Q-learning). We implemented Q-Learning in two primary ways: first, through the more classical table storage mechanism, and second, by training a neural net to learn the Q-function approximated by the table.


### To Run:

python main.py <-numSimulations>
  
  numSimulations (optional): an int representing the number of trials to complete before displaying to the screen (speeds up training considerably)

### Dependencies:
- keras
- pygame
- numpy
- matplotlib
- sklearn
  
### Codebase overview:

- main.py: main entrypoint into program
- car.py: class which simulates a car with a set of sensors
- obstacle.py: class which simulates a square obstacle that can be instantiated to follow some path of circular motion
- geometry.py: helper file which contains basic geometry functions (used to compute sensor/object and sensor/boundary intersections
- baseqlearner.py: base implementation of table-based q learning
- qlearnermodrandom.py: implementation of table-based q learning with modification to random selections
- qnn.py: implementation of neural-net-based q learning
- chart_creator.py: helper script used to generate charts and basic statistics on results

NOT USED IN FINAL IMPLEMENTATION (but included in repo for completeness):
- neuralnet.py: from-scratch implementation of neural net
- qlearner.py: attempt at incorporating neural nets into q-learning pipeline


### Resources:
- https://en.wikipedia.org/wiki/Q-learning
- https://studywolf.wordpress.com/2012/11/25/reinforcement-learning-q-learning-and-exploration/
- http://iamtrask.github.io/2015/07/12/basic-python-network/
- https://github.com/dennybritz/nn-from-scratch
- http://outlace.com/Reinforcement-Learning-Part-3/
- Mnih, Volodymyr, et al. "Playing atari with deep reinforcement learning." arXiv preprint arXiv:1312.5602 (2013).
- Bing-Qiang Huang, Guang-Yi Cao and Min Guo, "Reinforcement Learning Neural Network to the Problem of Autonomous Mobile Robot Obstacle Avoidance," 2005 International Conference on Machine Learning and Cybernetics, Guangzhou, China, 2005, pp. 85-89.
- https://www.youtube.com/watch?v=zOgSC---rgM
- https://www.youtube.com/watch?v=0Str0Rdkxxo

