import sys
import os
import argparse

if __name__ == '__main__':
    """Entry point to interact with the commandline arguments"""
    main_parser = argparse.ArgumentParser(
        description="Simple program to do csv file pre-processing",
        epilog="Thank you for using",
        allow_abbrev=False,
    )
    main_parser.add_argument(
        "data_file",
        help="Name of the data file to be pre-processed",
        action='store',
    )
    main_parser.add_argument(
        '-v',
        '--version',
        action='version'
    )
    main_parser.parse_args()
