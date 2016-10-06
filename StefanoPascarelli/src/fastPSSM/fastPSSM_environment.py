import os
import sys
from subprocess import call



class ENVIRONMENT:

    #STATIC VARIABLES
    pfam = "/home/stefano/sweDATA/glob/pfam/"
    pfamscan = "/home/stefano/sweDATA/glob/Pfamscan/pfam_scan.pl"
    pfam_database_dimension = "28332677"
    uniprot_trembl = "/home/stefano/sweDATA/glob/uniprot/uniprot_trembl.fasta"  # to do: check for it and db bin creator
    test = True

    def __init__(self):

        self.pfam = ENVIRONMENT.pfam
        self.pfamscan = ENVIRONMENT.pfamscan
        self.uniprot = ENVIRONMENT.uniprot_trembl
        self.dbdimension = ENVIRONMENT.pfam_database_dimension
        self.input_file = ""
        self.psiblast = False
        self.jackhmmer = True
        self.output_folder = ""
        self.verbose = False
        self.stdout = open("/dev/null","w+")
        self.paramK = True  # param Kostas (for doing something when reduced DB is void)

        #  CHECKS
        if self.test:
            a = self.check_bash()

            b = self.check_python()

            c = self.check_hmmer()

            d = self.check_pfam()

            e = self.check_pfamscan()

            f = self.check_psiblast()

            if not (a and b and c and d and e and f):
                sys.exit("CHECKS WENT WRONG")

        #DEFAULT PARAMETERS
        self.param_pfamscan = [" 10 ", " -clan_overlap "] # DEFAULTS
        # [e-val threshold,clan-overlap]

        self.param_jackhmmer = ["3", " --incT 25 "]  # DEFAULTS
        # [N of iterations, bitscore inclusion threshold (around 0.1 e-val)]

        self.param_psiblast = ["3", " -evalue 0.1 ", ""]  # DEFAULTS
        # [N of iter, eval default threshold, default outformat

#  CHECKS
    def check_bash(self):
        return True

    def check_python(self):

        try:
            from Bio import SeqIO
        except:
            sys.exit("Error in configuring BIO-python"+str(sys.exc_info()))
        return True


    def check_hmmer(self):

        print(">>> TESTING jackhmmer PRESENCE <<<")
        try:
            std = self.stdout
            if self.verbose:
                std = None
            retcode = call("jackhmmer",stdout = std)
            print "DONE!\n"
        except OSError as e:
            sys.exit("ERROR: hmmer not found as bash command")

        return True


    def check_pfam(self):

        print(">>> TESTING pfam folder FILES <<<\n")

        pfamfiles = next(os.walk(self.pfam))
        print(str(pfamfiles))
        print("")

        return True


    def check_pfamscan(self):

        print(">>> TESTING Pfamscan.pl PRESENCE <<<\n")
        try:
            #cehckstustuf
            std = self.stdout
            if self.verbose:
                std = None
            retcode = call(self.pfamscan,stdout=std)
            print("Done!\n")
        except OSError as e:
            sys.exit("ERROR: pfamscan.pl not found or didn't work")
        return True

    def check_psiblast(self):

        print(">>> TESTING psiblast PRESENCE <<<\n")
        try:
            std = self.stdout
            if self.verbose:
                std = None
            retcode = call("psiblast",stdout=std)
            print("Done!\n")
        except OSError as e:
            sys.exit("ERROR: psiblast not found as bash command")

        return True


c = ENVIRONMENT()