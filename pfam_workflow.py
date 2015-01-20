import sys
import os
import time
from Bio import SeqIO

def main(args):
    inFile = args[1]
    outDir = args[2] 
    blastDir = args[3] #"/scratch/chrisp/tools/blast-2.2.26/"
    if os.path.exists(outDir) is False:
        os.mkdir(outDir)

    #os.system("./fix_fasta.pl $fastafile > $tmpdir/query.fa");
    # We need to check if the fasta file is valid.

    with open(inFile, "rU") as seqFile:
        for entry in list(SeqIO.parse(seqFile, "fasta")):
            tmpDir = outDir + entry.id + "/"

            if os.path.exists(tmpDir) is False:
                os.mkdir(tmpDir)

            with open(tmpDir + "query.fa", "w") as outFile:
                outFile.write(">" + str(entry.id) + "\n" + str(entry.seq))

            os.system("./fa2prfs_pfamscan.sh " + tmpDir + " " + blastDir);


            #Run predictors here

if __name__=="__main__":
    main(sys.argv)

