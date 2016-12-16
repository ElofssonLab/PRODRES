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
    parser.add_argument('--input', dest="input_file", required=True, help='input file that needs to be in fasta format, can be one or more sequences')
    parser.add_argument('--output', required=True, help='the path to the output folder. The folder will be created if it does not exist already.')
    parser.add_argument('--second-search', required=True, choices=['psiblast', 'jackhmmer'])
    parser.add_argument('--paramK', default=True, help='The paramK flag. TODO write more documentation.')
    # Do we get better error handling out of the box if make use
    # of "type=file" for the directory path and file path options?
    parser.add_argument('--pfam-dir', required=True, type=str, help='pfam dir path')
    parser.add_argument('--uniprot-db-fasta', required=True, type=str, help='path to uniprot_db fasta file')
    parser.add_argument('--pfam_database_dimension', type=int, default=47230144, help="dimension of pfam database") #old dim: 28332677
    parser.add_argument("--verbose", action='store_true', help="output more information")
    parser.add_argument('--threads', type=str, default=None, help="number of threads (CPUs) to be used in second search")

    # Pfamscan parameters
    parser.add_argument('--pfamscan-script', required=True, type=str, help='path to pfam_scan.pl')
    parser.add_argument('--pfamscan_e-val', default=None, type=str, help='e-value threshold for pfamscan passage, usage: --pfamscan_e-val 0.1')
    parser.add_argument('--pfamscan_bitscore', default="2", type=str, help='bit-value threshold for pfamscan passage, usage: --pfamscan_bitscore 5')
    parser.add_argument('--pfamscan_clan-overlap', default=True, help='enable pfamscan resolve clan overlaps ')

    # Jackhmmer parameters
    parser.add_argument('--jackhmmer_max_iter', type=str, default="3", help='set the maximum number of iterations for jackhmmer')
    parser.add_argument('--jackhmmer_e-val', type=str, default=None, help='set the e-value threshold for jackhmmer, usage: --jackhmmer_e-val 0.1')
    parser.add_argument('--jackhmmer_bitscore', type=str, default="25.0", help='set the bitscore threshold for jackhmmer (jackhmmer option --incT), usage: --jackhmmer_bitscore 10')
    parser.add_argument('--jackhmmer-threshold-type', choices=['e-value', 'bit-score'])

    # Psiblast parameters
    parser.add_argument('--psiblast_iter', type=str, default="3", help='set the number of iterations for psiblast')
    parser.add_argument('--psiblast_e-val', type=str, default="0.1", help='set the e-value threshold for psiblast, usage: --psiblast_e-val 0.1')
    parser.add_argument('--psiblast_outfmt', type=str, help='set the outformat for psiblast, refer to blast manual')

    return parser


def verify_consistency_of_arguments(args):
    """Verify that the command line are logically correct."""
    if (args.jackhmmer_e_val != None and args.jackhmmer_bitscore != None):
        raise RuntimeError("both --jackhmmer_e-val and --jackhmmer_bitscore can not be specified at the same time")
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
        a["jackhmmer_bitscore"] = None
    if a.get("pfamscan_bitscore",False):
        a["pfamscan_e-val"] = None

    verify_consistency_of_arguments(args)
    verify_readable_file_path(args.uniprot_db_fasta)
    verify_readable_directory_path(args.pfam_dir)
    verify_program_available_in_path_directories("jackhmmer")
    verify_program_available_in_path_directories("psiblast")
    verify_program_available_in_path_directories("python")

    # Some sanity checks but ignore the returned output
    subprocess.check_output(["jackhmmer", "-h"])
    subprocess.check_output(["psiblast", "-help"])
    subprocess.check_output(["python", "--version"])
    # PFAMSCAN TEST MODIFIED TO FILE EXISTANCE
    #try:
    #    subprocess.Popen(["sh","-c",args.pfamscan_script,"-h",">/dev/null"])
    #except subprocess.CalledProcessError as e:
    #    raise RuntimeError("{}>>Problem detected executing pfamscan.pl test, did you check all its dependencies?<<".format(e.output))
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

    # Right now --verbose does not change anything.
    # Maybe we could let it change the logging leve like this?
    #
    # if args.verbose:
    #    log_level = logging.DEBUG

    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.basicConfig(filename='logs/{}run.log'.format(datetime.datetime.today()), level=log_level, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.warning('Started PRODRES pipeline with the following args:\n{}'.format(" ".join(argv)))

    logging.info('\t> Environment testing...')
    print("Beginning Environment testing...")

    print("Ending Environment testing.")
    logging.info('\t> End.')

#    logging.info('\t> Input parsing...')
#    print("Beginning input parsing...")

#    inp = INPUT_PARSER(argv, args)

#    print("Ending input parsing.")
#    logging.info('\t> End.')
# ???
    logging.info('\t> CDR...')

    with open(args.input_file,"rU") as seqFile:
        inpt = list(SeqIO.parse(seqFile, "fasta"))
        length = len(inpt)
        if length <=0:
            sys.exit("ERROR IN READING INPUT FILE!")
        print("\t>>>Sequences found: "+str(length)+" <<<\n")
        print("Beginning CDR...")
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
