#!/usr/bin/python


import sys, getopt,re
import os
import linecache
from random import randrange
import myfunc
import StringIO
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SearchIO
#from Bio.SearchIO import HmmerIO
#from Bio.SeqFeature import SeqFeature, FeatureLocation
from pprint import pprint

pfam_Dir = "/pfs/nobackup/home/a/arnee/FastPSSM/data/Pfam/"
pfamseqdb = "/pfs/nobackup/home/a/arnee/FastPSSM/data/pfamfull/uniref100.pfam27.pfamseq.nr90"
#pfamScan = "/home/a/arnee/FastPSSM/bin/PfamScan/pfam_scan.pl"
# Perhaps better to us pfamScan than hmmscan ??

cutoff=0.001
seqdir="data/"
resdir="results/"
PfamDB=pfam_Dir+"Pfam-A.hmm"



def ReadHitDB(pfamList):
    hdl = myfunc.MyDB(pfamseqdb)
    hitsdict ={}
    if hdl.failure:
        print "Error"
        return 1
    for pfamid in pfamList:
        print pfamid
        record=[]
        record=hdl.GetRecord(pfamid)
        if record:
          #name=outFile.write(record)
          #print record
            for line in StringIO.StringIO(record):
                if (line[0] == ">"):
                    name=re.sub(r'\s.*','',line)
                    hitsdict[name]=1
    return hitsdict
    hdl.close()


def main(argvs):
    File=sys.argv[1]
    name=re.sub(r'.*\/','',File)
    name=re.sub(r'\..*','',name)
    specie=re.sub(r'^\w+\/','',File)
    specie=re.sub(r'\/.*','',specie)
   
    HitsDomtab=resdir+"/"+specie+"/"+name+".domtab"
    SeqFile=seqdir+"/"+specie+"/"+name+".fa"
    SeqDomtab=seqdir+"/"+specie+"/"+name+".domtab"
    SeqOut=seqdir+"/"+specie+"/"+name+".out"


#handle = open(SeqFile, 'rU')
#print "opening "+ SeqFile +"\n"
#SeqRecord=SeqIO.parse(handle, 'fasta')

    if (not os.path.isfile(SeqDomtab)):
        os.system("hmmscan --cpu 4 --domtblout " + SeqDomtab  +  "  -o  " + SeqOut + "  "+ PfamDB + " " + SeqFile )

    query=[]
    for record in SearchIO.parse(SeqDomtab, 'hmmscan3-domtab') :
        for target in record:
            for hit in target:
                if (target.evalue < cutoff):         
               # print target.accession, target.evalue
                    query.append(re.sub(r'\..*','',target.accession))
  
    PfamHitsDB=ReadHitDB(list(set(query)))
    NumHitsDB=len(PfamHitsDB)
    TP=0
    FP=0 
#print "opening "+ HitsDomtab +"\n"
# For each record (mitochrodrial genome, in this case)...
    for record in SearchIO.parse(HitsDomtab, 'hmmscan3-domtab') :
#for record in SearchIO.parse(file, 'hmmer3-text') :
        for target in record:
#      print "\n\n **** target ****\n\n"
#      print target
#      print "\n\n **** info ****\n\n"

            found = False
            pfam=[]
            for word in target.description.split():
                if word[:2] == "PF":
                    pfam.append(re.sub(r'\,.*','',word))
                    found = False
            for q in query:
                for p in pfam:
               #            print p,q
                    if (q == p):
                        found=True
            

#      print "HIT: ", target.id, target.evalue, target.bitscore, found, target.description
            if (found):
                TP=TP+1
            else:
                FP=FP+1

            print target.id, target.evalue, target.bitscore, float(float(TP)/(float(TP)+float(FP))),TP, FP, NumHitsDB,found


if __name__ == "__main__":
    main(sys.argv)
