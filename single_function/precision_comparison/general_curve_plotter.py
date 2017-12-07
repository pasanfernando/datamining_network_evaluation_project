'''This is a general code that reads multiple dictionaries and plot their curves in the same plot
for comparison purposes.

For instances, it can be used to compare the ROC curves for different networks'''

import matplotlib.pyplot as plt
from operator import itemgetter
from collections import OrderedDict
import numpy as np

# A method to read the dictionary and storing it in x and y lists
# this method can be used to threshold was metric kind of plots; e.g: precision vs threshold

def dicreader(filename):
    x=[]
    y=[]
    hash1 ={}
    dicfile = open(filename, 'r')
    for line in dicfile:
        if line !='\n':
            a = line.strip().split('\t')
            hash1[float(a[0])]=float(a[1])

    hash1 = OrderedDict(sorted(hash1.items(), key=lambda t: t[0]))
    for i in hash1:
        x.append(i)
        y.append(hash1[i])

    return x,y

x1,y1 = dicreader('uberon_0000033precision_hash.txt')
x2,y2 = dicreader('uberon_0001944precision_hash.txt')

plt.title('Comparison of precision vs threshold curves')
plt.xlabel('Threshold')
plt.ylabel('Precision')

plt.plot(x1, y1, label='head')
plt.plot(x2, y2, label='pretectal region')
plt.xlim(xmax=750)
plt.legend()

plt.savefig('precision_comparison.jpg')




