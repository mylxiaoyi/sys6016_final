class Obstacle():

	def __init__(self, _p1, _p2, _p3, _p4):
		self.p1 = _p1
		self.p2 = _p2
		self.p3 = _p3
		self.p4 = _p4

	def get_lines(self):
		return [(self.p1, self.p2),
				(self.p2, self.p3),
				(self.p3, self.p4),
				(self.p4, self.p1)]



