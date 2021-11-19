from tabulate import tabulate
from lib.preprocessor import DataPreprocessor, FillType, NormalizationType
import argparse


def undefined(_):
    """ Handle undefined CLI interaction """
    print("run the program again with -h flag for more information")


def list_func(list_args):
    """ Handle list info CLI interaction """
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
    """Handle fill N/A CLI interaction"""
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
    """Handle delete duplicate data CLI interaction"""
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


def delete_with_threshold(delthres_args):
    """ Handle delete with threshold CLI interaction"""
    processor = DataPreprocessor(delthres_args.file)
    if delthres_args.outfile:
        if not delthres_args.outfile.endswith('.csv'):
            raise NameError("output filename must end with '.csv'")
    if delthres_args.type == 'row':
        print("deleting missing rows with a given threshold...")
        processor.delete_missing_row(threshold=delthres_args.threshold_int,
                                     threshold_pct=delthres_args.threshold_percentage,
                                     file_name=delthres_args.outfile)
    elif delthres_args.type == 'col':
        print("deleting missing attributes with a given threshold...")
        processor.delete_missing_column(threshold=delthres_args.threshold_int,
                                        threshold_pct=delthres_args.threshold_percentage,
                                        file_name=delthres_args.outfile)
    if delthres_args.outfile:
        print(f"Saved to {delthres_args.outfile}")
    else:
        print(f"Saved to {delthres_args.file}")
    print("done!")


def normalization(norm_args):
    """ Handle normalization on a NUMERIC attribute CLI interaction"""
    processor = DataPreprocessor(norm_args.file)
    if norm_args.outfile:
        if not norm_args.outfile.endswith('.csv'):
            raise NameError("output filename must end with '.csv'")
    if norm_args.type == 'min-max':
        print("performing min-max normalization...")
        processor.normalization(attribute=norm_args.attribute, normalization_type=NormalizationType.MIN_MAX,
                                file_name=norm_args.outfile)

    elif norm_args.type == 'z-score':
        print("performing z-score normalization...")
        processor.normalization(attribute=norm_args.attribute, normalization_type=NormalizationType.Z_SCORE,
                                file_name=norm_args.outfile)

    if norm_args.outfile:
        print(f"Saved to {norm_args.outfile}")
    else:
        print(f"Saved to {norm_args.file}")
    print("done!")


def attribute_calculation(calc_args):
    """ Handle attributes calculations on a NUMERIC attribute CLI interaction"""
    processor = DataPreprocessor(calc_args.file)
    if calc_args.outfile:
        if not calc_args.outfile.endswith('.csv'):
            raise NameError("output filename must end with '.csv'")
    processor.attributes_calculation(calc_str=calc_args.calc_string, col_name=calc_args.attribute_name,
                                     file_name=calc_args.outfile)
    if calc_args.outfile:
        print(f"Saved to {calc_args.outfile}")
    else:
        print(f"Saved to {calc_args.file}")
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
    # missing_cols(self) -> Dict[str, list]
    # count_missing_rows(self) -> int
    list_parser = sub_parsers.add_parser("list",
                                         help="list the information about data such as missing cols, missing rows,...")
    list_parser.add_argument('-mr', '--missing-rows', help="list missing rows", action='store_true')
    list_parser.add_argument('-mc', '--missing-cols', help="list missing columns", action='store_true')
    list_parser.add_argument('-m', '--missing', help="list missing info", action='store_true')
    list_parser.set_defaults(func=list_func)

    # fill nan value: 3
    # fill_nan(self, numeric_fill: FillType, fall_back: str = '0', file_name: str = None) -> None
    fill_parser = sub_parsers.add_parser("fill", help="fill the missing N/A value of the data with specified type")
    fill_parser.add_argument("-ft", '--filltype',
                             help="set the fill type for NUMERIC value, must be one of [mean, median]", required=True,
                             choices=["mean", "median"], metavar='')
    fill_parser.add_argument("-fb", "--fallback", help="set fallback value if fill failed, default value will be '0'",
                             metavar='', default='0')
    fill_parser.add_argument("-o", "--outfile",
                             help="set the name of the output file, if not specified, the current file will be "
                                  "overwritten", metavar='')
    fill_parser.set_defaults(func=fill_na_func)

    # delete with threshold: 4, 5
    # delete_missing_column(self, threshold: int = 1, threshold_pct: float = None, file_name: str = None) -> None
    # delete_missing_row(self, threshold: int = 1, threshold_pct: float = None, file_name: str = None) -> None
    delete_with_threshold_parser = sub_parsers.add_parser('delthres',
                                                          help="delete missing rows or columns given a threshold")
    delete_with_threshold_parser.add_argument('-t', '--type', choices=['row', 'col'],
                                              help='type of deletion to performed, on attributes (col) or rows (row),'
                                                   ' must be one of ["row", "col"]',
                                              required=True, metavar='')
    delete_with_threshold_parser.add_argument('-ti', '--threshold-int', type=int, default=1,
                                              help="threshold to delete using count, "
                                                   "if missing rows or cols is bigger than this threshold, "
                                                   "it will be deleted, default to 1 ", metavar='')
    delete_with_threshold_parser.add_argument('-tp', '--threshold-percentage', type=float,
                                              help="threshold to delete using percentage, "
                                                   "if missing rows or cols is bigger than this threshold, "
                                                   "it will be deleted, threshold-int will be ignored if this is set, "
                                                   "the float value must be between 0-1",
                                              metavar='')
    delete_with_threshold_parser.add_argument("-o", "--outfile",
                                              help="set the name of the output file, if not specified, the current "
                                                   "file will be overwritten", metavar='')
    delete_with_threshold_parser.set_defaults(func=delete_with_threshold)

    # delete duplicate: 6
    # delete_duplicate_row(self, file_name: str = None) -> None
    delete_duplicate_parser = sub_parsers.add_parser("deldup", help="delete duplicate data")
    delete_duplicate_parser.add_argument('-t', '--type', choices=['row'],
                                         help='choose the type of duplicate deletion, must be one of ["rows"]',
                                         metavar='', required=True)
    delete_duplicate_parser.add_argument("-o", "--outfile",
                                         help="set the name of the output file, if not specified, the current file "
                                              "will be overwritten", metavar='')
    delete_duplicate_parser.set_defaults(func=delete_duplicate)

    # normalization: 7
    # normalization(self, attribute: str, normalization_type: NormalizationType, file_name: str = None) -> None
    norm_parser = sub_parsers.add_parser('norm', help="perform normalization on a given NUMERIC attribute")
    norm_parser.add_argument('-t', '--type', choices=['min-max', 'z-score'], required=True,
                             help="select the type of normalization, must be one of ['min-max', 'z-score']", metavar='')
    norm_parser.add_argument('-a', '--attribute', required=True,
                             help="name of a given NUMERIC attribute to perform normalization", metavar='')
    norm_parser.add_argument("-o", "--outfile",
                             help="set the name of the output file, if not specified, the current file "
                                  "will be overwritten", metavar='')
    norm_parser.set_defaults(func=normalization)

    # attribute calc: 8
    # attributes_calculation(self, calc_str: str, col_name: str = None, file_name: str = None) -> None
    attribute_calc_parser = sub_parsers.add_parser('acalc',
                                                   help='perform attributes calculations on NUMERIC attributes')
    attribute_calc_parser.add_argument('-c', '--calc-string', required=True,
                                       help="operations to perform, must contain correct attribute names in the data, "
                                            "only support + - * / ex: (atr1 + atr2) * atr3", metavar='')
    attribute_calc_parser.add_argument('-a', '--attribute-name',
                                       help='name of the attribute to store calculations results, if not specified, '
                                            'the calc-string will be used as the new attribute\'s name', metavar='')
    attribute_calc_parser.add_argument("-o", "--outfile",
                                       help="set the name of the output file, if not specified, the current file "
                                            "will be overwritten", metavar='')
    attribute_calc_parser.set_defaults(func=attribute_calculation)

    # run the parser
    args = main_parser.parse_args()
    args.func(args)
