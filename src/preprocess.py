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


if __name__ == '__main__':
    """Entry point to interact with the commandline arguments"""

    # Main parser, do general stuff
    main_parser = argparse.ArgumentParser(description="Simple program to do csv file pre-processing",
                                          epilog="Thank you for using", allow_abbrev=False, )
    main_parser.add_argument('-f', '--file', help="Name of the data file to be pre-processed", action='store',
                             required=True, metavar='')
    main_parser.add_argument('-v', '--version', action='version', version='preprocessor version 1.0.0', )
    main_parser.set_defaults(func=undefined)
    sub_parser = main_parser.add_subparsers(help="use <option> -h to view more info", )
    # show info about rows and cols: 1, 2
    list_parser = sub_parser.add_parser("list")
    list_parser.add_argument('-mr', '--missing-rows', help="list missing rows", action='store_true')
    list_parser.add_argument('-mc', '--missing-cols', help="list missing columns", action='store_true')
    list_parser.add_argument('-m', '--missing', help="list missing info", action='store_true')
    list_parser.set_defaults(func=list_func)

    # fill nan value: 3
    fill_parser = sub_parser.add_parser("fill")
    fill_parser.add_argument("-ft", '--filltype',
                             help="Set the fill type for NUMERIC value, must be one of [mean, median]", required=True,
                             choices=["mean", "median"], metavar='')
    fill_parser.add_argument("-fb", "--fallback", help="Set fallback value if fill failed, default value will be 0",
                             metavar='', default='0')
    fill_parser.add_argument("-o", "--outfile",
                             help="Set the name of the output file, if not specified, the current file will be "
                                  "overwritten", metavar='')
    fill_parser.set_defaults(func=fill_na_func)

    # delete with threshold: 4, 5

    # delete duplicate: 6

    # standardization: 7

    # attribute calc

    # run the parser
    args = main_parser.parse_args()
    args.func(args)
