'''This code reads in the all function stat file that has AUC values and generates
different graphs'''

import collections
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss

__author__ = 'Pasan Fernando'
# 3 lists to store each column
roc =[]
pr =[]
frequency =[]

statfile = open('pre_processed_stats.txt', 'r')

# lisr ri store functions with zero AUC
zerofunctions = []
for line in statfile:

    if line != '\n':
        if 'function' not in line:
            a = line.strip().split('\t')
            #if a[0] != 'function':
            # removing the functions with 0 AUC; remove this if condition if you want to keep them
            if float(a[2])!=0:
                frequency.append(float(a[1]))
                roc.append(float(a[2]))
                pr.append(float(a[3]))

            else:
                zerofunctions.append(a[0])

print zerofunctions
#print frequency
print 'range for ROC:',min(roc),max(roc)
print 'range for pr:',min(pr),max(pr)
print 'range for frequency:',min(frequency),max(frequency)

print 'pearson correlation for roc:',np.corrcoef(frequency,roc)

print 'pearson correlation for PR:',np.corrcoef(frequency,pr)

print ss.pearsonr(frequency,roc)
print ss.pearsonr(frequency,pr)

plt.xlabel('Number of gene annotations')
plt.ylabel('The area under the curve for ROC')
plt.title('The area under the curve for ROC vs number of gene annotations')


plt.ylim(0,1.1)
plt.scatter(frequency,roc)
#xmin,xmax=plt.xlim()
plt.xlim(xmin=0)

# fitting a regression line
x = np.array([min(frequency),max(frequency)])
a, b = np.polyfit(np.array(frequency), np.array(roc), deg=1)
f = lambda x: a*x + b
plt.plot(x,f(x), "k--", label="y = "+str(round(a,4))+'x + '+str(round(b,4)))
plt.legend(loc=4)

plt.savefig('ROCvsf.jpg')
#plt.show()
plt.close()

plt.xlabel('Number of gene annotations')
plt.ylabel('The area under the curve for precision-recall curves')
plt.title('The area under the curve for precision-recall curves vs number of gene annotations')
plt.scatter(frequency,pr, color='green')
plt.ylim(0,1.1)

#xmin,xmax=plt.xlim()
plt.xlim(xmin=0)
# fitting a regression line
x = np.array([min(frequency),max(frequency)])
a, b = np.polyfit(np.array(frequency), np.array(pr), deg=1)
f = lambda x: a*x + b
plt.plot(x,f(x), "k--", label="y = "+str(round(a,4))+'x + '+str(round(b,4)))
plt.legend(loc=4)

plt.savefig('prvsf.jpg')
#plt.show()
plt.close()


plt.hist(roc,100)
plt.xlabel('The area under the curve for ROC')
plt.ylabel('Frequency')
plt.title('Histogram for the area under the curve of ROC')
#plt.show()
plt.xlim(0,1)
plt.savefig('rochist.jpg')
plt.close()

# histogram for the auc of PR curve
plt.hist(pr,100, color='green')
plt.xlabel('The area under the curve of precision-recall curve')
plt.ylabel('Frequency')
plt.title('Histogram for the area under the curve of precision-recall curve')
plt.xlim(0,1)
#plt.show()
plt.savefig('prhist.jpg')
plt.close()

# histogram for the auc of number of gene annotations curve
plt.hist(frequency,100, color='red')
plt.xlabel('Number of gene annotations')
plt.ylabel('Frequency')
plt.title('Histogram for number of the gene annotations')
#plt.show()
plt.savefig('annotationhist.jpg')
plt.close()