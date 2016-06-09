import os
import sys
from Bio import SeqIO


def INPUT_PARSER(argv,env):

        input = []

        ############### argv handling ################
        paramlist = []
        for param in argv[1:]:
            if param.startswith("--"):
                paramlist.append(param[2:])
            else:
                paramlist.append(param)

        # INPUT FILE
        input_file = False
        if "input" in paramlist:
            env.input_file = paramlist[paramlist.index("input")+1]
            paramlist.remove(env.input_file)
            paramlist.remove("input")

        # SECOND SEARCH TYPE
        if "psiblast" in paramlist:
            env.psiblast = True
            env.jackhmmer = False
            paramlist.remove("psiblast")
        if "jackhmmer" in paramlist:
            env.psiblast = False
            env.jackhmmer = True
            paramlist.remove("jackhmmer")

        # pfamscan PARAMETERS
        if "pfamscan_e-val" in paramlist:
            env.param_pfamscan[0] = paramlist[paramlist.index("pfamscan_e-val") + 1]
            paramlist.remove(env.param_pfamscan[0])
            paramlist.remove("pfamscan_e-val")

        if "pfamscan_clan-overlap" in paramlist:
            if paramlist[paramlist.index("pfamscan_clan-overlap") + 1] == "F":
                env.param_pfamscan[1] = ""
            paramlist.remove(env.param_pfamscan[1])
            paramlist.remove("pfamscan_clan-overlap")

        # jackhmmer PARAMETERS
        if "jackhmmer_iter" in paramlist:
            iter = paramlist[paramlist.index("jackhmmer_iter") + 1]
            env.param_jackhmmer[0] = iter
            paramlist.remove(iter)
            paramlist.remove("jackhmmer_iter")

        if "jackhmmer_e-val" in paramlist:
            eval = paramlist[paramlist.index("jackhmmer_e-val") + 1]
            env.param_jackhmmer[1] = " --incE "+eval+" "
            paramlist.remove(eval)
            paramlist.remove("jackhmmer_e-val")

        if "jackhmmer_bitscore" in paramlist:
            bs = paramlist[paramlist.index("jackhmmer_bitscore") + 1]
            env.param_jackhmmer[1] = " --incT " + bs + " "
            paramlist.remove(bs)
            paramlist.remove("jackhmmer_bitscore")

        # OUTPUT FOLDER
        if "output" in paramlist:
            env.output_folder = paramlist[paramlist.index("output") + 1]
            if not os.path.exists(env.output_folder):
                os.makedirs(env.output_folder)
            paramlist.remove(env.output_folder)
            paramlist.remove("output")

        #### ARGV failure output ####
        if len(paramlist)!=0 or len(argv)<2 or env.input_file == "" or env.output_folder == "":
            sys.exit("ARGV: "+str(argv)+"""
            >>>fastPSSM pipeline<<<
            usage: python fastPSSM.py <param>

            parameters:
                --input <input file>:                   needs to be in fasta format, can be one or more sequences [**]
                --output <output folder>:               the path to the output folder [**]
                --psiblast / --jackhmmer:               option to decide the second search to be performed (by default it is hmmer)
                --pfamscan_e-val <e-value>:             e-value threshold for pfamscan passage (default is 10)
                --pfamscan_clan-overlap <T/F>:          set clan-overlap parameter of pfamscan (default is True)
                --jackhmmer_iter <# of iterations>:     set the number of iterations for jackhmmer (default is 3)
                --jackhmmer_e-val <e-value>:            set the e-value threshold for jackhmmer
                --jackhmmer_bitscore <bitscore>:        set the bitscore threshold for jackhmmer (default is 25)
            [**] = compulsory parameter

            example call:""")

        ##### inputfile parsing #####
        with open(env.input_file,"rU") as seqFile:
            input = list(SeqIO.parse(seqFile, "fasta"))
            length = len(env.input_file)
            if length <=0:
                sys.exit("ERROR IN READING INPUT FILE!")
            print("\t>>>Sequences found: "+str(length)+" <<<\n")

        return input