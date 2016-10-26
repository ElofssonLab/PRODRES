import sys
from PRODRES_environment import ENVIRONMENT
from PRODRES_parser import INPUT_PARSER
from PRODRES_search import PROTEIN_DOMAIN_REDUCED_SEARCH
import logging
import datetime
import os
def main(argv):

    print("""
    #########################################################################################
    #########                                                                       #########
    #########                            PRODRES PIPELINE                           #########
    #########                                                                       #########
    #########################################################################################
    """)



#  MANAGEMENT OF PARAMETERS

    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.basicConfig(filename='logs/{}run.log'.format(datetime.datetime.today()), level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.warning('Started PRODRES pipeline with the following args:\n{}'.format(" ".join(argv)))

    logging.info('\t> Environment testing...')
    print("Beginning Environment testing...")

    env = ENVIRONMENT()

    print("Ending Environment testing.")
    logging.info('\t> End.')

    logging.info('\t> Input parsing...')
    print("Beginning input parsing...")

    inp = INPUT_PARSER(argv,env)

    print("Ending input parsing.")
    logging.info('\t> End.')

    logging.info('\t> PROtein Domain REduced Search...')
    print("Beginning PROtein Domain REduced Search...")

    PROTEIN_DOMAIN_REDUCED_SEARCH(env, inp)

    print("Ending CDR.")
    logging.info('\t> End.')
    logging.warning('Pipeline ended')

if __name__ == '__main__':
    main(sys.argv)
