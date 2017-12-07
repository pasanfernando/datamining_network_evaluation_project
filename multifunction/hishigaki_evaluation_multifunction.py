import networkx as nx
from collections import defaultdict
from operator import itemgetter
from collections import OrderedDict
import numpy as np

import curve_plotter as cp

__author__ = 'Pasan Fernando'
#import matplotlib.pyplot as plt

""" Code to gene function prediction based on the hishigaki methods
    This code is for evaluation using leave one out method
    The evaluation method for multiple classes/ functions is newly proposed
    
    Note: if you feel there is some thing wrong with the code, please uncomment the print statements throughout 
    the code. It will print results for each step. Do this with the prototype.
    """

############################################################################# ###########


#methods for calculating evaluation metrics

def evaluation_metrics(p,n,tp,tn,fp,fn):

    # calculating the accuracy
    try:
        accuracy = (tp+tn)/float(p+n)
    except ZeroDivisionError:
        accuracy = 0
    #print 'Accuracy is:',accuracy

    #error rate
    try:
        error_rate = (fp+fn)/float(p+n)
    except ZeroDivisionError:
        error_rate = 0
    #print 'Error rate is:', error_rate

    #sensitivity/ same as recall
    try:
        sensitivity = tp/float(p)
    except ZeroDivisionError:
        sensitivity = 0
    #print 'sensitivity:', sensitivity

    #specificity
    try:
        specificity = tn/float(n)
    except ZeroDivisionError:
        specificity = 0
    #print 'specificity:', specificity

    #precision
    try:
        precision = tp/float(tp+fp)
    except ZeroDivisionError:
        precision=0
    #print 'precision:', precision

    #true positive rate
    try:
        tpr = tp/float(p)
    except ZeroDivisionError:
        tpr=0

    # false positive rate
    try:
        fpr = fp/float(n)
    except ZeroDivisionError:
        fpr=0

    # false positive rate

    return accuracy,error_rate,sensitivity,specificity,precision,tpr,fpr


########################################################################################

#input1 = raw_input('enter the interaction file:')
#input2 = raw_input('enter the genelist file:')

# creating a nested dictionary to store chi square values for different functions for each gene
chigenes = defaultdict(dict)

#Reading the input gene function relations file

genelist = open('zebrafish_anatomy_profiles.txt', 'r')

# defining a multiple dictionary to store functions: genes
genefunc = defaultdict(list)
# defining a multiple dictionary to store gene: functions
genedic = defaultdict(list)

# Then convert the above input file into function: gene format

# this indicator is required for leave one out method

# reading the gene file
for line in genelist:
    if line != '\n':
        line = line.strip()
        a = line.split('\t') # splitting the line by tab to separate gene name vs functions
        if a[1] != 'gene_name': # excluding the header
            a[1] = a[1].lower()  # convert to lower case to avoid mismatches
            # print a[0]
            # here, we are evaluating, so only the proteins with functions will be considered
            if len(a) > 1:  # ths is required because there are proteins without one single function
                b = a[3].split(',')  # seperating the functions by comma
                # store each function in the multi dic by function as the key and genes as values
                for i in b:
                    genedic[a[1]].append(i)  # this dictionary stores genes as keys
                    genefunc[i].append(a[1])

print genedic
print genefunc

# ### reading the network file########################################################
in1 = open('zebranetwork700.txt', 'r')
G = nx.Graph()
for line in in1:
    if line != '\n':
        #print line
        if 'combined_score' not in line:
            line = line.strip('\n')
            a = line.split()
            #print a[0],a[1],a[2]
            G.add_edge(a[0].lower(),a[1].lower(), weight = a[2])

# visualizing the network; please turn this off when loading large networks
# nx.draw_networkx(G, with_labels=True)
# plt.draw()
# plt.show()

######### calculate the function frequency or phi #########
# total proteins in the network
totps = nx.number_of_nodes(G)

# total proteins for the given function
# funps = len(genelist) # you are assuming all genes matches the ones in the network; need to check one by one

genes_in_network = nx.nodes(G)
print 'genes in the network:',genes_in_network
genes_not_found = []
for gene in genedic:
    print 'gene is:', gene
    #print 'gene is:',gene

    #dictionaries to store total and function counts, chi square value
    total={}
    ccount={}
    chisq = {}

    #counting the genes with given function in immediate neighborhood of gene in consideration in leave one out method

    # going through the different functions in the function list
    for i in genefunc:
        #print 'function is:',i
        genelist = genefunc[i]
        #print genelist

        # making sure the gene in question is removed from the gene list because we are assuming it does not have any function
        if gene in genelist:
            # removing the gene by list comprehension; otherwise it will mutate the original dictionary
            genelist = [x for x in genelist if x != gene]
        #print genelist
        #print genefunc[i]

        # making sure all the genes in the input data file are in the network

        notfound = set(genelist) - set(genes_in_network)  # genes that are not found in the network
        #print 'genes that are not found in the network:', notfound
        found = set(genelist) & set(genes_in_network)  # genes that are found in the network
        #print 'genes that are found in the network:', found


        funps = len(found)

        fracps = float(funps) / totps

        #print fracps

        # counting the genes with given function in immediate neighborhood of gene in consideration in leave one out method
        totalc =0 # initially, total count is zero
        ccountc=0 # initially, neighborhood count is zero
        if gene in G:
            nb = nx.all_neighbors(G, gene)
            #print i
            for j in nb:
                #print j
                totalc=totalc+1 # counting the total neighbors; could have done this using len(nb) as well
                if j in genelist: # if the neighbor is in the gene list that neghbor has the function
                    ccountc=ccountc+1

            # storing the above calculated values in designated dictionaries
            total[i]=totalc
            ccount[i]=ccountc

            #calculate expected frequency values
            ef = fracps*totalc
            # calculating the chi-square value
            try: # this error handling is required to avoid zero division when ef=0
                chi = ((ccountc-ef)**2)/ef
            except ZeroDivisionError:
                chi = 0
            chisq[i] = chi
            chigenes[gene] = chisq
        else:
            genes_not_found.append(gene)

    #print chisq
    #print total
    #print ccount

    chigenes[gene]=chisq



# print chigenes
# print chigenes['p1']

# ordering each dictionary based on the highest function

for i in chigenes:
    chigenes[i]= OrderedDict(sorted(chigenes[i].items(),key=lambda t:t[1], reverse=True))
    #print chigenes[i]

print chigenes

# a list to store chivalues; used to get the maximum chi value
chivalues = []
############################################################################################
# writing the predicted gene functions in an output file in sorted order
out = open('predicted_functions.txt', 'wb+')
out.write('genes\tpredicted_functions\n')

for i in chigenes:
    out.write('%s\t'%(i))
    func_chi = chigenes[i]
    lastelement = list(func_chi.keys())
    #print lastelement[-1]
    for j in func_chi:
        #print j
        chivalues.append(float(func_chi[j]))# appending chi values
        if j == lastelement[-1]:# this avoids printing a comma after the last element
            out.write('%s:%s' % (j, func_chi[j]))
        else:
            out.write('%s:%s,'%(j,func_chi[j]))

    out.write('\n')
out.close()



###########################################################################################
# module to calculate FP,TP,TN, FN

# defining dictionaries to store evaluation metrics for each threshold value
accuhash ={}
errorhash ={}
sensehash ={}
specifichash ={}
precisionhash ={}

# one multi dictionary to store fpr and tpr for thresholods
# the key should be the threshold
rochash = defaultdict(list)

# another hash for prescision recall curve
precision_recall_hash = defaultdict(list)

for threshold in np.arange(0,(max(chivalues)+1),0.2):
    #threshold use as the cutoff to draw the roc curve
    #threshold = 0

    # defining the variables
    pcountfinal =0
    ncountfinal =0
    tpcountfinal =0
    tncountfinal =0
    fpcountfinal =0
    fncountfinal =0

    # getting total functions as a set
    totfunc = set(genefunc.keys())
    #print 'all the functions:',totfunc



    for i in chigenes:
        pred_functions =[] # list to store functions higher than the threshold
        genefunctions = chigenes[i]
        for j in genefunctions:
            if float(genefunctions[j])>=threshold: # if the chi value is greater than the threshold append it to the list
                pred_functions.append(j)

        #print pred_functions
        pred_functions = set(pred_functions) # converting to set for comparisons
        # predicted negatives
        pred_negatives = totfunc - pred_functions

        # obtaining actual positives and actual negatives (P and N in standard notation)
        act_positives =set(genedic[i])  # reading from genedic dictionary to obtain original data
        #print 'actual positives:',act_positives
        p = len(act_positives)
        pcountfinal = pcountfinal + p  # adding to the parent variable that sums positive count for all the genes

        act_negatives = totfunc - act_positives
        #print 'actual negatives:', act_negatives
        n = len(act_negatives)
        ncountfinal = ncountfinal + n
        #print act_positives

        #calculate TP
        tp = pred_functions & act_positives
        #print 'TP:', tp
        tpcount = len(tp)
        tpcountfinal = tpcountfinal + tpcount

        #calculate FP
        fp = pred_functions - act_positives
        #print 'FP:', fp
        fpcount = len(fp)
        fpcountfinal = fpcountfinal + fpcount

        # calculate TN
        tn = pred_negatives & act_negatives
        tncount = len(tn)
        tncountfinal = tncountfinal + tncount

        # calculate FN
        fn = pred_negatives - act_negatives
        fncount = len(fn)
        fncountfinal = fncountfinal + fncount


    # print 'P:', pcountfinal
    # print 'N:',ncountfinal
    # print 'TP:',tpcountfinal
    # print 'TN:',tncountfinal
    # print 'FP:',fpcountfinal
    # print 'FN:',fncountfinal

    # getting all the evaluation metrics including the tpr and fpr
    accuracy,error_rate,sensitivity,specificity,precision,tpr,fpr= evaluation_metrics(pcountfinal,ncountfinal,tpcountfinal,tncountfinal,fpcountfinal,fncountfinal)

    # storing metrics in defined dictionaries
    accuhash[threshold]=accuracy
    errorhash[threshold]=error_rate
    sensehash[threshold]=sensitivity
    specifichash[threshold]=specificity
    precisionhash[threshold]=precision

    rochash[threshold].append(fpr)
    rochash[threshold].append(tpr)

    #if sensitivity != 0:
    precision_recall_hash[threshold].append(sensitivity)
    precision_recall_hash[threshold].append(precision)

print rochash
print precision_recall_hash



print max(chivalues)

cp.ROCplotter(rochash,'roc')
cp.ROCplotter(precision_recall_hash,'precision_recall')
cp.metric_plotter(accuhash,'Accuracy')
cp.metric_plotter(errorhash,'Error_rate')
cp.metric_plotter(sensehash,'Sensitivity')
cp.metric_plotter(specifichash,'Specificity')
cp.metric_plotter(precisionhash,'Precision')

preciout = open('precision_hash.txt','wb+')
rocout = open('roc_hash.txt','wb+')

for i in rochash:
    a = rochash[i]
    rocout.write('%s\t%s\t%s\n'%(i,a[0],a[1]))

for i in precision_recall_hash:
    a = precision_recall_hash[i]
    preciout.write('%s\t%s\t%s\n'%(i,a[0],a[1]))