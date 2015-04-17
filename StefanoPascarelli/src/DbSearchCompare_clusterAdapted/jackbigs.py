#!/bin/python

import os
import sys
import time

Bitscore=" --incE 0.01 "


flag=sys.argv[1]
query=sys.argv[2]
outdir=sys.argv[3]
dbpath=sys.argv[4]



if flag =='1':
# print flag
#print " - start fast jackhmmer" 
 timeout=outdir+"/fastHMM/" 
 if os.path.exists(outdir+"/fastHMM/") is False:
  os.mkdir(outdir+"/fastHMM/")
#time output
 timeout=open(outdir+"/fastHMM/timelog.txt","w")
 timeout.write("job_start: %.3f"%time.time())

 outfile=outdir+"/fastHMM/tableOut.txt"
 dbfile=outdir+"/QUERY.hits.db"
 aligfile=outdir+"/fastHMM/Alig.txt"
 fullout=outdir+"/fastHMM/fullout.txt"
# hmmout=outdir+"/fastHMM/HMMout.txt"
 if os.path.exists(outfile) is False:
  os.system("jackhmmer -N 3 --noali --cpu 16 -o "+fullout+Bitscore+"--tblout "+outfile+" -A "+aligfile+" -Z 28332677 "+query+" "+dbfile)
 timeout.write("\tjob_end: %.3f"%time.time())
# print " - end fast"
# else:
#  print " - skipped, tableOut.txt already present"

#jackhammer on full database
else:
# print flag
 #print " - start slow jackhmmer"
 if os.path.exists(outdir+"/slowHMM/") is False:
  os.mkdir(outdir+"/slowHMM/")
#time output
 timeout=open(outdir+"/slowHMM/timelog.txt","w")
 timeout.write("job_start: %.3f"%time.time())
 outfile=outdir+"/slowHMM/tableOut.txt"
 dbfile=dbpath+"/pfam_seqdb.txt"
 aligfile=outdir+"/slowHMM/Alig.txt"
 fullout=outdir+"/slowHMM/fullout.txt"
# hmmout=outdir+"/slowHMM/HMMout.txt"
 if os.path.exists(outfile) is False:
  os.system("jackhmmer -N 3 --noali --cpu 16 -o "+fullout+Bitscore+"--tblout "+outfile+" -A "+aligfile+" -Z 28332677 "+query+" "+dbfile)
 timeout.write("\tjob_end: %.3f"%time.time())
# print " - end slow"
#else:
# print " - skipped, tableOut.txt already present"

