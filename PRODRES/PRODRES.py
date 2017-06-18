import sys
from PRODRES_CDR import COMMON_DOMAINS_REDUCTION
import logging
import datetime
import os
import shutil
import argparse
from Bio import SeqIO
import subprocess

def create_parser(argv):
    """Create a command line parser with all arguments defined."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, fromfile_prefix_chars='@')

    # General parameters
    parser.add_argument("--verbosity",type=int, help="verbosity level", default=1)
    parser.add_argument('--input', dest="input_file", required=True, help='input file that needs to be in fasta format, can be one or more sequences')
    parser.add_argument('--output', required=True, help='the path to the output folder. The folder will be created if it does not exist already.')
    parser.add_argument('--second-search', required=True, choices=['psiblast', 'jackhmmer'])
    parser.add_argument('--paramK', default=True, help='The paramK flag. TODO write more documentation.')
    parser.add_argument('--force-fallback', default=False, help='if True, forces fallback search instead of PRODRES search')
    parser.add_argument('--pfam-dir', required=True, type=str, help='pfam dir path')
    parser.add_argument('--fallback-db-fasta', required=True, type=str, help='path to uniprot_db fasta file')
    parser.add_argument('--prodres-db', default="/prodres_db.nr100.sqlite3", help='path to prodres database')
    parser.add_argument('--pfam_database_dimension', type=int, default=56526462, help="dimension of pfam database") #refers to Uniprot 2016_2
    parser.add_argument('--threads', type=str, default=None, help="number of threads (CPUs) to be used in second search")
    parser.add_argument('--parallel', type=int, default=None, help="in case of a multifasta file, enable parallel job submission. int for number of parallel processes ")
    parser.add_argument('--force-override', default=False, help="change to anything if you want to force override of output folder")

    # Pfamscan parameters
    parser.add_argument('--pfamscan-script', required=True, type=str, help='path to pfam_scan.pl')
    parser.add_argument('--pfamscan_e-val', default=None, type=str, help='e-value threshold for pfamscan passage, usage: --pfamscan_e-val 0.1')
    parser.add_argument('--pfamscan_bitscore', default="2", type=str, help='bit-value threshold for pfamscan passage, usage: --pfamscan_bitscore 5')
    parser.add_argument('--pfamscan_clan-overlap', default=True, type=bool, help='enable pfamscan resolve clan overlaps [True,False]')

    # Jackhmmer parameters
    parser.add_argument('--jackhmmer_max_iter', type=str, default="3", help='set the maximum number of iterations for jackhmmer')
    parser.add_argument('--jackhmmer_e-val', type=str, default=None, help='set the e-value threshold for jackhmmer, usage: --jackhmmer_e-val 0.1')
    parser.add_argument('--jackhmmer_bit-score', type=str, default="25.0", help='set the bit-score threshold for jackhmmer (jackhmmer option --incT), usage: --jackhmmer_bit-score 10')
    parser.add_argument('--jackhmmer-threshold-type', choices=['e-value', 'bit-score'])

    # Psiblast parameters
    parser.add_argument('--psiblast_iter', type=str, default="3", help='set the number of iterations for psiblast')
    parser.add_argument('--psiblast_e-val', type=str, default="0.1", help='set the e-value threshold for psiblast, usage: --psiblast_e-val 0.1')
    parser.add_argument('--psiblast_outfmt', type=str, help='set the outformat for psiblast, refer to blast manual')

    return parser


def verify_consistency_of_arguments(args):
    """Verify that the command line are logically correct."""
    if (args.jackhmmer_e_val != None and args.jackhmmer_bit_score != None):
        raise RuntimeError("both --jackhmmer_e-val and --jackhmmer_bit-score can not be specified at the same time")
    if (args.second_search == 'jackhmmer' and args.jackhmmer_threshold_type == None):
        raise RuntimeError("--jackhmmer-threshold-type is missing (required by --second-search=jackhmmer)")


def verify_file_path(path):
    """Verify that the path is a file."""
    if not os.path.isfile(path):
        raise RuntimeError('Not a file path: {}'.format(path))


def verify_readable_file_path(path):
    """Verify the file is readable."""
    verify_file_path(path)
    if not os.access(path, os.R_OK):
        raise RuntimeError('The path does not have the read file permission: {}'.format(path))


def verify_directory_path(path):
    """Verify that the path is a directory path."""
    if not os.path.isdir(path):
        raise RuntimeError('The path is not a directory: {}'.format(path))


def verify_readable_directory_path(path):
    """Verify that the path is a readable directory path."""
    verify_directory_path(path)
    if not os.access(path, os.R_OK):
        raise RuntimeError('The path does not have the read file permission: {}'.format(path))


def verify_writable_directory_path(path):
    """Verify that the path is a readable directory path."""
    verify_directory_path(path)
    if not os.access(path, os.W_OK):
        raise RuntimeError('The path does not have the write file permission: {}'.format(path))


def verify_program_available_in_path_directories(program_name):
    """Verify that the program name is available in the environment PATH directories."""
    prog =  subprocess.check_output(["which",program_name])
    #   shutils.which is woking only in python 3+, while db handling python code is written in 2.7
    if prog == None:
        raise RuntimeError('The program is not available in the enviroment PATH directories: {}'.format(path))


def main(argv):
  try:
    parser = create_parser(argv)
    args = parser.parse_args()
    # fix with parser mutually exclusive maybe?
    a = vars(args)
    if a.get("jackhmmer_e_val",False):
        a["jackhmmer_bit_score"] = None
    if a.get("pfamscan_bit_score",False):
        a["pfamscan_e-val"] = None

    verify_consistency_of_arguments(args)
    verify_readable_file_path(args.fallback_db_fasta)
    verify_readable_directory_path(args.pfam_dir)
    try:
        verify_readable_file_path(args.prodres_db)
    except RuntimeError:
        args.prodres_db = args.pfam_dir + args.prodres_db
        verify_readable_file_path(args.prodres_db)
    
    verify_program_available_in_path_directories("jackhmmer")
    verify_program_available_in_path_directories("psiblast")
    verify_program_available_in_path_directories("python")

    # Some sanity checks but ignore the returned output
    subprocess.check_output(["jackhmmer", "-h"])
    subprocess.check_output(["psiblast", "-help"])
    subprocess.check_output(["python", "--version"])
    verify_readable_file_path(args.pfamscan_script)

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    verify_writable_directory_path(args.output)

    print("""
    #########################################################################################
    #########                                                                       #########
    #########                             PRODRES PIPELINE                          #########
    #########                                                                       #########
    #########################################################################################
    """)


    log_level = logging.INFO
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.basicConfig(filename='logs/{}run.log'.format(datetime.datetime.today()), level=log_level, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.warning('Started PRODRES pipeline with the following args:\n{}'.format(" ".join(argv)))

#    logging.info('\t> Environment testing...')
#    print("Beginning Environment testing...")

#    print("Ending Environment testing.")
#    logging.info('\t> End.')
#    logging.info('\t> CDR...')
    with open(args.input_file,"rU") as seqFile:
        inpt = list(SeqIO.parse(seqFile, "fasta"))
        length = len(inpt)
        if length <=0:
            sys.exit("ERROR IN READING INPUT FILE!")
        print("\t>>>Sequences found: "+str(length)+" <<<\n")
        print("Beginning CDR...")
        if args.parallel:
            # parallel computing
            print("commencing parallel computation")
            logging.warning("commencing parallel computation")
            from multiprocessing import Pool
            pool = Pool(processes=args.parallel)
            for item in inpt:
                pool.apply_async(COMMON_DOMAINS_REDUCTION,args=(args,[item]))
            pool.close()
            pool.join()
        else:
            COMMON_DOMAINS_REDUCTION(args, inpt)

    print("Ending CDR.")
    logging.info('\t> End.')
    logging.warning('Pipeline ended')
  except IOError as e:
    print("I/O error: {0}".format(e))
  except RuntimeError as e:
    print("Runtime error: {0}".format(e))
  except:
    print("Unexpected error")
    raise

if __name__ == '__main__':
    main(sys.argv)
