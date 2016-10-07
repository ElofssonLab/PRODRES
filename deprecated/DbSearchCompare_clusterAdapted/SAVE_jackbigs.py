#!/bin/python

import os
import sys
import time

Bitscore=" --incE 0.1 "


flag=sys.argv[1]
query=sys.argv[2]
outdir=sys.argv[3]
dbpath=sys.argv[4]



if flag in ['1','2','3','4']:
# print flag
#print " - start fast jackhmmer" 
 timeout=outdir+"/fastHMMparam"+flag+"/" 
 if os.path.exists(outdir+"/fastHMMparam"+flag+"/") is False:
  os.mkdir(outdir+"/fastHMMparam"+flag+"/")
#time output
 timeout=open(outdir+"/fastHMMparam"+flag+"/timelog.txt","w")
 timeout.write("job_start: %.3f"%time.time())

 outfile=outdir+"/fastHMMparam"+flag+"/tableOut.txt"
 dbfile=outdir+"/param"+flag+".hits.db"
 aligfile=outdir+"/fastHMMparam"+flag+"/Alig.txt"
 fullout=outdir+"/fastHMMparam"+flag+"/fullout.txt"
# hmmout=outdir+"/fastHMM/HMMout.txt"
 if os.path.exists(outfile) is False:
  os.system("jackhmmer -N 3 --noali --cpu 2 -o "+fullout+Bitscore+"--tblout "+outfile+" -A "+aligfile+" -Z 28332677 "+query+" "+dbfile)
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
  os.system("jackhmmer -N 3 --noali --cpu 2 -o "+fullout+Bitscore+"--tblout "+outfile+" -A "+aligfile+" -Z 28332677 "+query+" "+dbfile)
 timeout.write("\tjob_end: %.3f"%time.time())
# print " - end slow"
#else:
# print " - skipped, tableOut.txt already present"

