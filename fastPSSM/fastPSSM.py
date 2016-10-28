import sys
from fastPSSM_CDR import COMMON_DOMAINS_REDUCTION
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
    parser.add_argument('--pfamscan_e-val', default="10.0", type=str, help='e-value threshold for pfamscan passage')
    parser.add_argument('--pfamscan_clan-overlap', default=True, help='enable pfamscan resolve clan overlaps ')
    parser.add_argument('--jackhmmer_max_iter', type=str, default="3", help='set the maximum number of iterations for jackhmmer')
    parser.add_argument('--jackhmmer_e-val', type=str, default=None, help='set the e-value threshold for jackhmmer')
    parser.add_argument('--jackhmmer_bitscore', type=str, default="25.0", help='set the bitscore threshold for jackhmmer (jackhmmer option --incT)')
    parser.add_argument('--psiblast_iter', type=str, default="3", help='set the number of iterations for psiblast')
    parser.add_argument('--psiblast_e-val', type=str, default="0.1", help='set the e-value threshold for psiblast')

    # A question:
    # Although --psiblast_outfmt is being listed as a command line option
    # in the file
    # https://github.com/ElofssonLab/FastPSSM/blob/a825496ed7bfdee30256a943fe3c6495c1265895/fastPSSM/fastPSSM_parser.py
    # the value given by the user is ignored in the code:
    # https://github.com/ElofssonLab/FastPSSM/blob/a825496ed7bfdee30256a943fe3c6495c1265895/fastPSSM/fastPSSM_CDR.py
    #
    # Should we have the
    # --psiblast_outfmt
    # option or not?
    #
    # Right now the option value is being used in the code

    parser.add_argument('--psiblast_outfmt', type=str, help='set the outformat for psiblast, refer to blast manual')
    parser.add_argument('--input', dest="input_file", required=True, help='input file that needs to be in fasta format, can be one or more sequences')
    parser.add_argument('--output', required=True, help='the path to the output folder. The folder will be created if it does not exist already.')
    parser.add_argument('--second-search', required=True, choices=['psiblast', 'jackhmmer'])
    parser.add_argument('--jackhmmer-threshold-type', choices=['e-value', 'bit-score'])
    parser.add_argument('--paramK', default=True, help='The paramK flag. TODO write more documentation.')
    # Do we get better error handling out of the box if make use
    # of "type=file" for the directory path and file path options?
    parser.add_argument('--pfam-dir', required=True, type=str, help='pfam dir path')
    parser.add_argument('--pfamscan-script', required=True, type=str, help='path to pfam_scan.pl')
    parser.add_argument('--uniprot-db-fasta', required=True, type=str, help='path to uniprot_db fasta file')
    parser.add_argument('--pfam_database_dimension', type=int, default=28332677, help="dimension of pfam database")
    parser.add_argument("--verbose", action='store_true', help="output more information")
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
    prog =  subprocess.check_output(["which", program_name])
    #   shutils.which is woking only in python 3+, while db handling python code is written in 2.7
    if prog == None:
        raise RuntimeError('The program is not available in the enviroment PATH directories: {}'.format(path))


def main(argv):
  try:
    parser = create_parser(argv)
    args = parser.parse_args()
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
    try:
        subprocess.check_output([args.pfamscan_script, "-h"]) != None
    except subprocess.CalledProcessError as e:
        raise RuntimeError("{}>>Problem detected executing pfamscan.pl test, did you check all its dependencies?<<".format(e.output))

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    verify_writable_directory_path(args.output)

    print("""
    #########################################################################################
    #########                                                                       #########
    #########                            FASTPSSM PIPELINE                          #########
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
    logging.warning('Started FASTPSSM pipeline with the following args:\n{}'.format(" ".join(argv)))

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
