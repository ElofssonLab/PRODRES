import sys
import os
import linecache
from random import randrange
import myfunc
import time

#
#pfamscan:"/home/stefano/git/FastPSSM/StefanoPascarelli/src/DbSearchCompare/Pfamscan/pfam_scan.pl"
#

flag=sys.argv[6]
pfam_Dir = sys.argv[3]
pfamseqdb = pfam_Dir+"/pfamfull/uniref100.pfam27.pfamseq.nr90"
pfamScan = "../Pfamscan/pfam_scan.pl"
Eval_tr=" -e_seq "+sys.argv[4]
Clan_overlap=""
if sys.argv[5]==True:
 Clan_overlap=" -clan_overlap "


def createHitDB(pfamList, prot_name, work_dir):
    hdl = myfunc.MyDB(pfamseqdb)
    if hdl.failure:
#        print "Error"
        return 1
    with open(work_dir + "param"+flag+".hits.db.temp", "w") as outFile:
        for pfamid in pfamList:
            record = hdl.GetRecord(pfamid)
            if record:
                outFile.write(record)
        hdl.close()

    os.system("python my_uniqueseq.py " + work_dir + "param"+flag+".hits.db.temp")


def main(argvs):


   input_file = argvs[1]
   work_dir = argvs[2]
   name_temp = (input_file[input_file.rfind("/")+1:])
   name = name_temp[:name_temp.rfind(".")]
#   print " - start pfamscan"
   if os.path.exists(work_dir + name + flag + ".txt") is False:
    #time output from pfamscan to DB end
    timeout=open(work_dir+"Pscantimelog"+flag+".txt","w")
    timeout.write("job_start: %.3f"%time.time()) 
    sCmd = "perl " + pfamScan + Clan_overlap + Eval_tr +" -fasta "+input_file + " -dir " + pfam_Dir + " -outfile " + work_dir + name + flag + ".txt"
    os.system(sCmd)

    pfamList = []
    pattern = "# <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>"
    bFoundStart = False
    with open(work_dir + name + flag + ".txt") as inFile:
        for line in inFile:
            if line.find(pattern) != -1:
                bFoundStart = True
            if bFoundStart is True:
                pos = line.find("PF")
                if pos != -1:
                    pfamList.append(line[pos:pos+7])

    createHitDB(list(set(pfamList)), name, work_dir)
    timeout.write("\tjob_end: %.3f"%time.time())
#   else:
#    print " - skipped, query.txt already present"

if __name__ == "__main__":
    main(sys.argv)
