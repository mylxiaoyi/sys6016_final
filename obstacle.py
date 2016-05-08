from math import sin,cos,pi, radians
from pygame.math import Vector2

class Obstacle():
	"""
	Obstacle class - used to represent squares moving around screen
	"""

	def __init__(self, _p1, width, height, _radius, init_deg):

		#initialize 4 points representing obstacle region
		self.p1 = _p1
		self.p2 = self.p1 + Vector2(width, 0.0)
		self.p3 = self.p1 + Vector2(width, height)
		self.p4 = self.p1 + Vector2(0.0, height)

		#necessary for angular motion
		self.radius = _radius
		self.angle = radians(init_deg)  #pi/4 # starting angle 45 degrees
		self.omega = -0.005 #Angular velocity

		#capture distances between p1 and other points
		self.p1_p2 = self.p2-self.p1
		self.p1_p3 = self.p3-self.p1
		self.p1_p4 = self.p4-self.p1

	def get_lines(self):
		"""
		Used to draw obstacles
		"""
		return [(self.p1, self.p2),
				(self.p2, self.p3),
				(self.p3, self.p4),
				(self.p4, self.p1)]

	def update(self, screen_dims):
		"""
		Update obstacle location
		Much of the angular motion code came from stackoverflow
		"""

		# Anchor point to be rotated around (center of screen)
		center_of_rotation_x = screen_dims[0]/2
		center_of_rotation_y = screen_dims[1]/2

		# New angle, we add angular velocity
		self.angle = self.angle + self.omega

		# New x
		self.p1[0] = self.p1[0] + (self.radius+10) * self.omega * cos(self.angle + pi / 2) 
		# New y
		self.p1[1] = self.p1[1] - (self.radius+10) * self.omega * sin(self.angle + pi / 2)

		# Update other points based off of new location of p1
		self.p2 = self.p1 + self.p1_p2
		self.p3 = self.p1 + self.p1_p3
		self.p4 = self.p1 + self.p1_p4
