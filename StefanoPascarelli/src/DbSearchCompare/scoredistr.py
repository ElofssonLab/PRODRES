#!/usr/bin/python

###remove triple hashtags for complete graph construction

import os,math,re,sys
import domtest
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import pylab


def scoregraphs(path,threshold):


 d=domtest.parsefile(path+"/slowHMM/tableOut.txt")
 num_bins=int(round(2*math.log(len(d.keys())+5),0)) 
 X=[]
 for val in d.values():
  if val[0]>threshold:
   X.append(val[0])
 print "len X is ",len(X)
 if len(X)!=0:
  n,bins,patches=plt.hist(X,num_bins,normed=0,facecolor="green",alpha=0.5)
  pylab.savefig(path+"/Graphs/"+str(threshold)+".png")
  pylab.clf()
 return X


def percentgraphs(path,threshold):

 with open(path+"/Score.txt") as inputfile:
  X=[]
  lines=inputfile.readlines()
  for index in range(len(lines)):
   if re.search(r"^"+str(threshold)+" ",lines[index])!=None:
    X=(int(lines[index+2].split()[0][:-3]),int(lines[index+1].split()[0][:-3]))
 
 if X!=[]:
  print threshold," found..."

# fast graph
  size=[X[0]]
  size.append(100-size[0])
  plt.pie(size,labels=["Catched","Missed"],colors=["lightblue","blue"],autopct='%1.1f%%')  
  plt.title("no. of sequences: "+str(X[1]))
  pylab.savefig(path+"/Graphs/fast"+str(threshold)+".png")
  pylab.clf()
 else:
  return

 return X



def main(argv):

 loc=argv[1]
 locE=loc+"/entry_collection/"
#plot of all data init
 total=[[]for i in range(4)]

#plot of total % results init
 totpercent=[[]for i in range(5)]

#plot of each entry 
 Y=next(os.walk(locE))[1]
 z=1
 for dirs in Y:
  if os.path.exists(locE+dirs+"/Graphs/") is False:
   os.mkdir(locE+dirs+"/Graphs/")
  print dirs,z,"/",len(Y)
  z+=1
  print "0< graph"
  total[0]+=scoregraphs(locE+dirs,0)
  print "50< graph"
  total[1]+=scoregraphs(locE+dirs,50)
  print "200< graph"
  total[2]+=scoregraphs(locE+dirs,200)
  print "400< graph"
  total[3]+=scoregraphs(locE+dirs,400)
  print "% graphs"
  for fufi in range(5):
   totpercent[fufi].append(percentgraphs(locE+dirs,fufi*50))


 #plot all data cont
 print "total graph"
 total.append([0,50,200,400])
 for i in range(4):
  n,bins,patches=plt.hist(total[i],max(1,math.pow(len(total[i]),1.0/5)),normed=0,facecolor="red",alpha=0.5)
  pylab.savefig(loc+"/statistics/"+str(total[4][i])+".png")
  pylab.clf()

 #plot percent data cont
 fast=[[],[]]
 for i in range(5):
  temps= []
  for x in totpercent[i]:
   if x!=None:
    temps.append(x[0])

  fast[0].append(np.mean(temps))
  fast[1].append(np.std(temps))

 N = 5

 ind = np.arange(N)  # the x locations for the groups
 width = 0.35       # the width of the bars

 fig, ax = plt.subplots()
 rects1 = ax.bar(ind, fast[0], width, color='r', yerr=fast[1])

# add some text for labels, title and axes ticks
 ax.set_ylabel('%')
 ax.set_title('Overlap percentage')
 ax.set_xticks(ind+width)
 ax.set_xticklabels( ('0', '50', '100', '150', '200') )

# ax.legend( (rects1[0]), ('Fast') )
 def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 0.90*height, '%d'%int(height),
                ha='center', va='bottom')


 autolabel(rects1)

# plt.show()
 pylab.savefig(loc+"/statistics/Overall%.png")
 pylab.clf()





if __name__=="__main__":
 main(sys.argv)
