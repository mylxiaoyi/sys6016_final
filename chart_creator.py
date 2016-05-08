# Small helper script for generating charts from output csv files
import matplotlib.pyplot as plt
import csv
import sys
import os
import numpy as np

#grab filename and chart title from command line args
filename = sys.argv[1]
title = sys.argv[2]

#generate x and y lists from csv
x = []
y = []

with open(os.path.join('./log_data', filename),'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
    	i = 0
    	for element in row:
	        if element != '':
	        	x.append(i)
	        	y.append(int(element))
	        	i += 1

# generate some statistics on the data
print "statistics"
print "mean: %s" % (np.mean(y))
print "std: %s" % (np.std(y))

#generate plot
plt.plot(x,y)
plt.xlabel('Trials')
plt.ylabel('Survival Time (Number of Frames)')
plt.title(title)
plt.legend()
plt.show()

