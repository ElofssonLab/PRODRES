#!/usr/bin/python

import os,re,numpy,sys





def parsefile(path):
 """returns dictionary of names, keys: [score,(pfam domains)]"""

 d={}

 with open(path) as infile:

  for row in infile.readlines():

    if row[0]!="#":

       split=row.split()
       name=split[0][11:]
       score=split[5]
       pfamdom=set()
       for elem in split[1:]:

         if elem[0:2]=="PF":
          pfamdom.add(elem[:7])
       d[name]=(float(score),name,list(pfamdom))

 return d


def scavengedomain(path):
 """gather domains from pfamscan output"""
 with open(path) as infile:
  s=set()

  for line in infile.readlines():
   if re.search(r"^[#\n]",line)==None:
    s.add(line.split()[5][:7])

 return s


def compare(d,fast,p):
 """count hits and total number of sequences in a matrix with this format: 3 rows, 1st line is total count, 2nd is fast hits count, 3rd is big hits count. coloumns are hits with score >0,>50,>100,>150,>200 (5 rows) """
 bad=[]
 m= [[0 for i in range(5)] for j in range(2)]

 for val in d.values():

  m[0][0]+=1
  if len(fast & set(val[2]))!=0:
   m[1][0]+=1

  if val[0]>50:
   m[0][1]+=1
   if len(fast & set(val[2]))!=0:
    m[1][1]+=1

   if val[0]>100:
    m[0][2]+=1
    if len(fast & set(val[2]))!=0:
     m[1][2]+=1

   if val[0]>150:
    m[0][3]+=1
    if len(fast & set(val[2]))!=0:
     m[1][3]+=1

    if val[0]>200:
     m[0][4]+=1
     if len(fast & set(val[2]))!=0:
      m[1][4]+=1


#save local informations
 o=open(p+"/Score.txt","w")
 for t in range(5):
  if m[0][t]!=0:
   stats=[[] for i in range (2)]
   stats[0]=(m[0][t]," counts\n")
   stats[1]=(float(m[1][t])*100/m[0][t]," % fast\n")
   o.write("%i statistics\n"%(t*50))
   o.write("%.2f%s"%stats[0])
   for st in stats[1:]:
    o.write("%.2f%s"%st)
    if st[0]<25:
     bad.append(t)
   o.write("\n\n")


 return m,bad



def computestats(outpath,megamatrix):
 """stats, what else. BTW stats=5 rows(>0,>50...>200) of a list of stats([average counts, devst, min and max, average fasthits, devst and min and max])"""

 stats=[[0.0 for i in range(8)]for j in range(5)]
#range max and min init
 cmaxes=[0.0 for i in range(5)]
 cmines=[20000.0 for i in range(5)]
 smaxes=[0.0 for i in range(5)]
 smines=[100.0 for i in range(5)]

#media and stdev temp var
 c_med_temp=[[] for i in range(5)]
 s_med_temp=[[] for i in range(5)]


 for matrix in megamatrix:

  for i in range(5):
#grab triplets of results each score filter
   counts=matrix[0][i]
   if counts!=0:
    fast_percent=round(float(matrix[1][i])*100/counts,3)

#compare max and min for range
    if counts > cmaxes[i]:
     cmaxes[i]=counts
    elif counts < cmines[i]:
     cmines[i]=counts

    if fast_percent>smaxes[i]:
     smaxes[i]=fast_percent
    elif fast_percent<smines[i]:
     smines[i]=fast_percent


#save of values for mean and st dev
    c_med_temp[i].append(counts)
    s_med_temp[i].append(fast_percent)

#end of per-matrix cycle

#computation of statistics
 for i in range(5):
  stats[i][0]=numpy.mean(c_med_temp[i])
  stats[i][1]=numpy.std(c_med_temp[i])
  stats[i][2]=cmines[i]
  stats[i][3]=cmaxes[i]
  stats[i][4]=numpy.mean(s_med_temp[i])
  stats[i][5]=numpy.std(s_med_temp[i])
  stats[i][6]=smines[i]
  stats[i][7]=smaxes[i]

#output

 with open(outpath,"w") as outfile:
  for i in range(5):
   yolo=tuple(stats[i])
   outfile.write("####################\n\nStatistics for scores > "+str(i*50)+"\n\n####################\n\n")
   outfile.write("average counts: %.0f\nst dev: %.1f\nrange: %.0f - %.0f\n\n\
fast pfamscan hits: %.2f %%\nst dev: %.2f\nrange: %.2f %% - %.2f %%\n\n\n\n"%yolo)

# print "The End, congratulations"


###### main #######
def main(argv):
#dic= parsefile("jackprova/Q96I45/slowBigProva.txt")
#print dic
 loc=argv[1]
 locE=loc+"/entry_collection/"
 hell=open(loc+"/statistics/hell.txt","w")
 matrixsave=[]
 z=1
 Y=next(os.walk(locE))[1]
 for dirs in Y:
  print dirs,z,"/",len(Y)
  z+=1
 #results from whole db jackhammer
  dic=parsefile(locE+dirs+"/slowHMM/tableOut.txt")
  print "computed dictionary of length ",len(dic.keys())

#domain found in pfamscan (s-mall and b-ig whether with or without -clan_overlap
  s=scavengedomain(locE+dirs+"/query.txt")
  print "found the following domains:\nfast pfamscan: "," ".join(s)

#comparison 
  print "begin comparison"
  M,flag=compare(dic,s,locE+dirs)
  matrixsave.append(M)

#bad guys go to hell
  if flag!=[]:
   hell.write(dirs+" "+str(flag)+" \n")


#saving dictionaries each folder
  outfile=open(locE+dirs+"/ParsedDic.txt","w")
  for val in dic.values():
   outfile.write("%10f %20s %30s \n"%val)

#saving domains of fast pfamscan
  outfile=open(locE+dirs+"/ParsedPfamscanDomains.txt","w")
  outfile.write("fast pfamscan domains: "+" ".join(s))

 print "beginning of statistics"
 stats = computestats(loc+"/statistics/overlap.txt",matrixsave)
 print "end of statistics"

if __name__ == "__main__":
 main(sys.argv)
