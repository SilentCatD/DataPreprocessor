import json
import sys
import os
from tabulate import tabulate
from lib.preprocessor import DataPreprocessor, FillType
import argparse


def undefined(_):
    print("run the program again with -h flag for more information")


def list_func(list_args):
    processor = DataPreprocessor(list_args.file)
    if list_args.missing:
        table = []
        data = processor.missing_cols()
        for key, value in data.items():
            table.append([key, len(value)])
        print("Generals missing data:")
        print(tabulate(table, headers=["attribute", "missing instance"], tablefmt='fancy_grid'))
    if list_args.missing_cols:
        table = []
        data = processor.missing_attributes()
        for attribute in data:
            table.append([attribute])
        print("Attribute with missing values")
        print(tabulate(table, headers=["attribute"], tablefmt='fancy_grid'))
    if list_args.missing_rows:
        data = processor.count_missing_rows()
        print(f"Number of rows with missing value: {data}")


def fill_na_func(fill_args):
    processor = DataPreprocessor(fill_args.file)
    if fill_args.outfile:
        if not fill_args.outfile.endswith('.csv'):
            raise NameError("output filename must end with '.csv'")
    if fill_args.filltype == 'mean':
        fill_type = FillType.MEAN
        print("mean")
    else:
        fill_type = FillType.MEDIAN
    print(f"filling N/A value with {fill_type.name}...")
    processor.fill_nan(numeric_fill=fill_type, fall_back=fill_args.fallback, file_name=fill_args.outfile)
    if fill_args.outfile:
        print(f"Saved to {fill_args.outfile}")
    else:
        print(f"Saved to {fill_args.file}")
    print("done!")


def delete_duplicate(deldup_args):
    print(vars(deldup_args))
    processor = DataPreprocessor(deldup_args.file)
    if deldup_args.outfile:
        if not deldup_args.outfile.endswith('.csv'):
            raise NameError("output filename must end with '.csv'")
    if deldup_args.type == 'row':
        print("deleting duplicate row...")
        processor.delete_duplicate_row(deldup_args.outfile)
    if deldup_args.outfile:
        print(f"Saved to {deldup_args.outfile}")
    else:
        print(f"Saved to {deldup_args.file}")
    print("done!")


if __name__ == '__main__':
    """Entry point to interact with the processor class, handle CLI"""

    # Main parser, do general stuff
    main_parser = argparse.ArgumentParser(description="Simple program to do csv file pre-processing",
                                          epilog="Thank you for using", allow_abbrev=False, )
    main_parser.add_argument('-f', '--file', help="name of the data file to be pre-processed", action='store',
                             required=True, metavar='')
    main_parser.add_argument('-v', '--version', action='version', version='preprocessor version 1.0.0', )
    main_parser.set_defaults(func=undefined)

    # add subparsers
    sub_parsers = main_parser.add_subparsers(help="use %(prog)s <option> -h to see usage of each option", )
    # show info about rows and cols: 1, 2
    list_parser = sub_parsers.add_parser("list",
                                         help="list the information about data such as missing cols, missing rows,...")
    list_parser.add_argument('-mr', '--missing-rows', help="list missing rows", action='store_true')
    list_parser.add_argument('-mc', '--missing-cols', help="list missing columns", action='store_true')
    list_parser.add_argument('-m', '--missing', help="list missing info", action='store_true')
    list_parser.set_defaults(func=list_func)

    # fill nan value: 3
    fill_parser = sub_parsers.add_parser("fill", help="fill the missing N/A value of the data with specified type")
    fill_parser.add_argument("-ft", '--filltype',
                             help="set the fill type for NUMERIC value, must be one of [mean, median]", required=True,
                             choices=["mean", "median"], metavar='')
    fill_parser.add_argument("-fb", "--fallback", help="Set fallback value if fill failed, default value will be '0'",
                             metavar='', default='0')
    fill_parser.add_argument("-o", "--outfile",
                             help="set the name of the output file, if not specified, the current file will be "
                                  "overwritten", metavar='')
    fill_parser.set_defaults(func=fill_na_func)

    # delete with threshold: 4, 5

    # delete duplicate: 6
    delete_duplicate_parser = sub_parsers.add_parser("deldup", help="delete duplicate data")
    delete_duplicate_parser.add_argument('-t', '--type', choices=['row'],
                                         help='Choose the type of duplicate deletion, must be one of ["rows"]',
                                         metavar='', required=True)
    delete_duplicate_parser.add_argument("-o", "--outfile",
                                         help="set the name of the output file, if not specified, the current file "
                                              "will be overwritten", metavar='')
    delete_duplicate_parser.set_defaults(func=delete_duplicate)
    # standardization: 7

    # attribute calc: 8

    # run the parser
    args = main_parser.parse_args()
    args.func(args)
