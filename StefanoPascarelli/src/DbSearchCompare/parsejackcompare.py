#!/usr/bin/python

import sys


##########COPIPASTAED CODE######

def parsenames(p,seqname):
   d={}
   with open(p) as f:
    for line in f.readlines():
       split=line.split()
       if len(split)>2:
        if split[2]==seqname:
             t_name=split[0]
             if "_" in t_name:
                 t_name=t_name[10:]
             name=t_name
             evalue=split[4]
             score=split[5]
             d[name]=[float(score),name,evalue]
   return d






####main####

def main(argv):

  tmpdir= argv[1]
  seqname=tmpdir[-7:-1]

  outfile=tmpdir+"Comparison.txt"
  out=open(outfile,"w")

  slow=tmpdir+"/slowHMM/tableOut.txt"
  fast=tmpdir+"/fastHMM/tableOut.txt"

#  sd,fd={},{}

  sdnames=parsenames(slow,seqname)
  fdnames=parsenames(fast,seqname)

  out.write("note: when not specified, slow dictionary results are on left, fast dictionary on right\n\n")

 #LENGTHS
  out.write("##################\nDictionary length: "+ str(len(sdnames.keys()))+" "+str(len(fdnames.keys()))+"\n##################\n")

 #TOP 15 names
  out.write("\nNames dictionary Top 15 scoring hits:\n")
  s,f=sorted(sdnames.values(),reverse=True),sorted(fdnames.values(),reverse=True)
  for i in range(15):
   out.write("{:>20} {:>10} {:>20} {:>10}".format(s[i][1],str(s[i][0]),f[i][1],str(f[i][0]))+"\n")

#### 2nd copypasta ####

 #slow non present in fast
  count=0
  s=sdnames.values()
  f=[]
  for val in fdnames.values():
   f.append(val[1]) 

  for value in s:
   if value[1] not in f:
    count=count+1
  out.write("\nSlow dictionary unique sequences: " +str(count))

 #fast non present in slow
  count=0
  f=fdnames.values()
  s=[]
  for val in sdnames.values():
   s.append(val[1])

  for value in f:
   if value[1] not in s:
    count=count+1
  out.write("\nFast dictionary unique sequences: " +str(count))


 #unique sequences over x=100 score in both lists
  count=0
  s=sdnames.values()
  f=[]
  for val in fdnames.values():
   if val[0]>100:
    f.append(val[1])

  for value in s:
   if value[1] not in f and value[0]>100:
    count=count+1
  out.write("\n\nSlow dictionary unique sequences over 100: " +str(count))
 #
  count=0
  f=fdnames.values()
  s=[]
  for val in sdnames.values():
   if val[0]>100:
    s.append(val[1])

  for value in f:
   if value[1] not in s and value[0]>100:
    count=count+1
  out.write("\nFast dictionary unique sequences over 100: " +str(count))

 #higher than 100
  count=0
  for f in fdnames.values():
   if f[0]>100:
    count=count+1
  out.write("\n\nFast seq score>100: "+str(count))
  #
  count=0
  for s in sdnames.values():
   if s[0]>100:
    count=count+1
  out.write("\nSlow seq score>100: "+str(count))

 #unique sequences over x=200 score in both lists
  count=0
  s=sdnames.values()
  f=[]
  for val in fdnames.values():
   if val[0]>200:
    f.append(val[1])

  for value in s:
   if value[1] not in f and value[0]>200:
    count=count+1
  out.write("\n\nSlow dictionary unique sequences over 200: " +str(count))
 #
  count=0
  f=fdnames.values()
  s=[]
  for val in sdnames.values():
   if val[0]>200:
    s.append(val[1])

  for value in f:
   if value[1] not in s and value[0]>200:
    count=count+1
  out.write("\nFast dictionary unique sequences over 200: " +str(count))

 #higher than 200
  count=0
  for f in fdnames.values():
   if f[0]>200:
    count=count+1
  out.write("\n\nFast seq score>200: "+str(count))
  #
  count=0
  for s in sdnames.values():
   if s[0]>200:
    count=count+1
  out.write("\nSlow seq score>200: "+str(count))





if __name__=="__main__":
 main(sys.argv)
