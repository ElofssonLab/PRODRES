import sys
from fastPSSM_environment import ENVIRONMENT_TEST
from fastPSSM_parser import INPUT_PARSER
from fastPSSM_CDR import COMMON_DOMAINS_REDUCTION


def main(argv):

    print("""
    #########################################################################################
    #########                                                                       #########
    #########                            FASTPSSM PIPELINE                          #########
    #########                                                                       #########
    #########################################################################################
    """)



#  MANAGEMENT OF PARAMETERS







    print("Beginning Environment testing...")

    env = ENVIRONMENT_TEST()

    print("Ending Environment testing.")


    print("Beginning input parsing...")

    inp = INPUT_PARSER(argv,env)

    print("Ending input parsing.")


    print("Beginning CDR...")

    COMMON_DOMAINS_REDUCTION(env,inp)

    print("Ending CDR.")


  #   print("Beginning second search...")
  #
  # #  SECOND_SEARCH()
  #
  #   print("Ending second search.")


if __name__ == '__main__':
    main(sys.argv)