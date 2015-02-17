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
  out.write("##################\nnames dictionary length "+ str(len(sdnames.keys()))+" "+str(len(fdnames.keys()))+"\n##################\n")

 #TOP 15 names
  out.write("\nNames dictionary Top 15 scoring hits:\n")
  s,f=sorted(sdnames.values(),reverse=True),sorted(fdnames.values(),reverse=True)
  for i in range(15):
   out.write("{:>20} {:>10} {:>20} {:>10}".format(s[i][1],str(s[i][0]),f[i][1],str(f[i][0]))+"\n")

if __name__=="__main__":
 main(sys.argv)
