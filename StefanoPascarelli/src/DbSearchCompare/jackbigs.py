#!/usr/bin/python

import os,sys

Bitscore=" --incT 250 "



query=sys.argv[1]
outdir=sys.argv[2]
dbpath=sys.argv[3]

#save## query[-15:-9],
#jackhammer on shrinked database

print " - start fast jackhmmer" 
if os.path.exists(outdir+"/fastHMM/") is False:
 os.mkdir(outdir+"/fastHMM/")
#condition to skip redos
if os.path.exists(outdir+"/fastHMM/tableOut.txt") is False:
 outfile=outdir+"/fastHMM/tableOut.txt"
 dbfile=outdir+"/query.hits.db"
 aligfile=outdir+"/fastHMM/Alig.txt"
 hmmout=outdir+"/fastHMM/HMMout.txt"
 os.system("time -o "+outdir+"/fasttime.txt jackhmmer -N 3 -o "+hmmout+Bitscore+"--tblout "+outfile+" -A "+aligfile+" -Z 28332677 "+query+" "+dbfile)
 print " - end fast"
else:
 print " - skipped, tableOut.txt already present"

#jackhammer on full database
print " - start slow jackhmmer"
if os.path.exists(outdir+"/slowHMM/") is False:
 os.mkdir(outdir+"/slowHMM/")
#condition to skip redos
if os.path.exists(outdir+"/slowHMM/tableOut.txt") is False:
 outfile=outdir+"/slowHMM/tableOut.txt"
 dbfile=dbpath+"pfam_seqdb.txt"
 aligfile=outdir+"/slowHMM/Alig.txt"
 hmmout=outdir+"/slowHMM/HMMout.txt"
 os.system("time -o "+outdir+"/slowtime.txt jackhmmer -N 3 -o "+hmmout+Bitscore+"--tblout "+outfile+" -A "+aligfile+" -Z 28332677 "+query+" "+dbfile)
 print " - end slow"
else:
 print " - skipped, tableOut.txt already present"

