import math
import os
import csv
from enum import Enum
from typing import Dict, List, AnyStr, Optional, Any, Tuple
from .xfix import EquationType, infix_to_postfix, type_of


class FillType(Enum):
    """
    Enum class define 3 main method of data fill

    ----

    These method will be used as data type to choose whether to fill a specific missing data with which method: mean,
    max, or median
    """
    MEAN = 0
    MEDIAN = 1
    MODE = 2


class NormalizationType(Enum):
    """
    Enum class define main types of normalization

    ----

    Min-max standardization or Z-score normalization to choose in normalizing a specific attribute
    """
    MIN_MAX = 0
    Z_SCORE = 1


class DataType(Enum):
    """
    Enum class define data type of each attribute

    ----

    Each attributes may belong to a specific type as defined here, those are:
        - NUMERIC for float value and such, can be used in mathematics expression
        - CATEGORICAL for named value, can't be calculated on
        - UNKNOWN for data type does not belong to above type
    """
    NUMERIC = 0
    CATEGORICAL = 1
    UNKNOWN = 2


class DataPreprocessor:
    """
    Main class to operate many data preprocessing method on a data file

    """

    def __init__(self, file: str, delimiter: str = ',') -> None:
        """
        Class constructor

        ----

        Input file name will be checked to see if such file truly exist, error will then be raise accordingly, the
        delimiter will be used in opening data file

        :param file: name of the data file
        :param delimiter: delimiter of each value in the file
        :raise: FileNotFoundError if the specified file is not available
        """
        if os.path.isfile(file):
            self._file = file
            self._delimiter = delimiter
        else:
            raise FileNotFoundError(f"The file '{file}' can't be found, please try again")

    def missing_cols(self) -> Dict[str, list]:
        """
        Function to determine attributes with missing values

        ----

        Open data file and loop through each rows, each cols to count and store information about missing columns,
        if a value is missing, attribute name of that value and list of missing rows numbers will be recorded

        :return: a dictionary which hold key-value pair:
                key: name of the attribute has missing value
                value: list of rows which has missing value of each attribute
        """
        missing_attribute = {}
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for row_number, csv_row in enumerate(csv_reader):
                row = dict(csv_row)
                for attribute in row.keys():
                    if row[attribute] == '':
                        if attribute in missing_attribute:
                            missing_attribute[attribute].append(row_number)
                        else:
                            missing_attribute[attribute] = [row_number]
        return missing_attribute

    def missing_rows(self) -> Dict[int, list]:
        """
        Function to determine attributes with missing values

        ----

        Open data file and loop through each rows, each cols to count and store information about missing rows

        |  If a value appear to be missing, the rows index and list of missing attribute will be recorded

         :return: a dictionary which hold key-value pair:
                key: row index of rows which has missing value, row index start at 0 and exclude fieldnames row
                value: list of attributes which is missing from this row
        """
        missing_rows = {}
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for row_number, csv_row in enumerate(csv_reader):
                row = dict(csv_row)
                for attribute in row.keys():
                    if row[attribute] == '':
                        if row_number in missing_rows:
                            missing_rows[row_number].append(attribute)
                        else:
                            missing_rows[row_number] = [attribute]
        return missing_rows

    def missing_attributes(self) -> List[AnyStr]:
        """
        Getter to get the missing attributes

        :return: list of attributes with missing value
        """
        return list(self.missing_cols().keys())

    def count_missing_rows(self) -> int:
        """
        Getter to count the missing rows

        :return: the number of rows with missing value
        """
        return len(self.missing_rows().keys())

    def _deter_data_type(self, attribute: str) -> DataType:
        """
        Determine the data type of a given attribute

        ----

        Loop through each attributes to deter it's type, utilize python value parse to see if that value can be parse
        into number or not.

        |  Though this only operate on attributes that has at least one value, attributes with no data
        will be determined as UnknownType

        :param attribute: name of the attribute
        :return: data type of this attribute
        :raise: Attribute error if there's no attribute with the given name
        """
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for csv_row in csv_reader:
                row = dict(csv_row)
                try:
                    if row[attribute]:
                        try:
                            float(row[attribute])
                            return DataType.NUMERIC
                        except ValueError:
                            return DataType.CATEGORICAL
                except KeyError as e:
                    raise AttributeError(f"No such attribute: {attribute}") from e
        return DataType.UNKNOWN

    def _standard_deviation(self, attribute: str) -> Optional[float]:
        """
        Function to calculate a standard deviation of a given attribute in a whole file, this will skip empty value

        ----

        Only operate on NUMERIC data type, return None if data type is not of this type

        |  Open the file and gather all value of given attribute to calculate standard deviation

        :param attribute: name of the NUMERIC attribute
        :return:
            float: standard deviation value of this attribute,
            None: if data type is not NUMERIC
        """

        if self._deter_data_type(attribute) != DataType.NUMERIC:
            return None

        mean = self._mean(attribute)
        total = 0.0
        has_value = 0
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for csv_row in csv_reader:
                row = dict(csv_row)
                if row[attribute]:
                    has_value += 1
                    total += math.pow(float(row[attribute]) - mean, 2)

        if has_value < 2:
            return 0
        return math.sqrt(total / (has_value - 1))

    def _mean(self, attribute: str) -> Optional[float]:
        """
        Function to calculate the mean of a given attribute, this will skip empty value

        ----

        Only operate on NUMERIC data type, return None if data type is not of this type

        |  Open the file and gather all value of given attribute to calculate mean

        :param attribute: name of the attribute
        :return:
                float: mean of the NUMERIC numeric attribute,
                None: if the attribute is not numeric
        """
        if self._deter_data_type(attribute) != DataType.NUMERIC:
            return None
        total = 0
        has_value = 0
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for csv_row in csv_reader:
                row = dict(csv_row)
                if row[attribute]:
                    has_value += 1
                    total += float(row[attribute])
        return total / has_value

    def _median(self, attribute: str) -> Optional[float]:
        """
        Function to calculate median of a given attribute, this will skip missing value

        ----

        Only operate on NUMERIC data type, return None if data type is not of this type

        |  Open the file and gather all value of given attribute to calculate median

        :param attribute: name of the NUMERIC attribute
        :return:
                float: value of the median of this attribute,
                None: if this attribute is not NUMERIC
        """
        if self._deter_data_type(attribute) != DataType.NUMERIC:
            return None
        values = []
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for csv_row in csv_reader:
                row = dict(csv_row)
                if row[attribute]:
                    values.append(row[attribute])
        middle_index = len(values) // 2
        return values[middle_index]

    def _mode(self, attribute: str) -> Optional[AnyStr]:
        """
        Function to calculate mode of a given attribute

        ----

        Only operate on data type different than UNKNOWN, return None if not this type

        |  Open the file and gather all value of given attribute to calculate mode

        :param attribute: name of the attribute
        :return:
                str: value of the mode of this attribute,
                None: if the attribute has all empty rows
        """
        if self._deter_data_type(attribute) == DataType.UNKNOWN:
            return None
        values = {}
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for csv_row in csv_reader:
                row = dict(csv_row)
                if row[attribute]:
                    if row[attribute] not in values:
                        values[row[attribute]] = 1
                    else:
                        values[row[attribute]] += 1
        values = sorted(values.items(), key=lambda item: item[1], reverse=True)
        return values[0][0]

    def _create_attribute_info(self, attribute: str, fall_back: str = '') -> Dict[AnyStr, Any]:
        """
        Function to generate a part of a lookup-table which hold value of missing attribute to avoid re-calculation

        ----

        Construct a lookup table for fill_nan function

        |  This lookup table will store value of mean, median, mode for NUMERIC value and mode for CATEGORICAL value

        :param attribute: name of this attribute
        :param fall_back: default value to fill if this attribute can't be calculated with: mean, mode, median
        :return:
                mean, mode, median for attribute of type NUMERIC,
                mode for attribute of type CATEGORICAL
        """
        attr_type = self._deter_data_type(attribute)
        info = {'type': attr_type}
        if attr_type == DataType.NUMERIC:
            mean = self._mean(attribute)
            median = self._median(attribute)
            mode = self._mode(attribute)
            info.update({'mean': mean if mean else fall_back,
                         'median': median if median else fall_back,
                         'mode': mode if mode else fall_back})
        elif attr_type == DataType.CATEGORICAL:
            mode = self._mode(attribute)
            info.update({'mode': mode if mode else fall_back})
        return {attribute: info}

    def _z_score(self, attribute: str) -> Tuple[List[Dict], List]:
        """
        Function to calculate value of z-score normalization on a given NUMERIC attribute

        ----

        Open the file to gather all data in it and add that data to a new data set

        |  This new data set will then be re-scaled with calculated mean and standard deviation

        :param attribute: name of the attribute
        :return:
                list: of a new data after calculation,
                list: fieldnames of this new data
        """
        new_data = []
        fieldnames = []
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            fieldnames.extend(csv_reader.fieldnames)
            for csv_row in csv_reader:
                row = dict(csv_row)
                new_data.append(row)
        mean = self._mean(attribute)
        standard_deviation = self._standard_deviation(attribute)
        for row in new_data:
            if row[attribute]:
                row[attribute] = (float(row[attribute]) - mean) / standard_deviation
        return new_data, fieldnames

    def _min_max(self, attribute: str) -> Tuple[List[Dict], List]:
        """
        Function to calculate value of min-max normalization on a given NUMERIC attribute

        ----

        Open the file to gather all data in it and add that data to a new data set

        |  This new data set will then be re-scaled with  mean-max normalization method

        :param attribute: name of the attribute
        :return:
                list: of a new data after calculation
                list: fieldnames of this new data
        """
        values = []
        same_values = False
        new_data = []
        fieldnames = []
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            fieldnames.extend(csv_reader.fieldnames)
            for csv_row in csv_reader:
                row = dict(csv_row)
                new_data.append(row)
                if row[attribute]:
                    values.append(float(row[attribute]))
        _min = min(values)
        _max = max(values)
        if _max == _min:
            same_values = True

        for row in new_data:
            if row[attribute]:
                if same_values:
                    row[attribute] = 0
                else:
                    row[attribute] = (float(row[attribute]) - _min) / (_max - _min)
        return new_data, fieldnames

    def fill_nan(self, numeric_fill: FillType, fall_back: str = '0', file_name: str = None) -> None:
        """
        Function to perform data fill with the specified FillType

        ----

        Open the file to gather it's data and treat missing data with specified FillType

        | To avoid repeated re-calculation each time a missing value is encountered, a look-up table will be constructed

        |  Filled data will be stored in a new data set and get saved with specified file name, if not specified, this
        new data will overwritten old data in old data file

        :param numeric_fill: option to fill NUMERIC data, this may be mode, mean, and median,
                             categorical data will always fill by mode
        :param fall_back: default data to put into cell if this fill operation failed
        :param file_name: name of the file to save this data
        """
        attribute_fill = {}
        filled_data = []
        fieldnames = []
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            fieldnames.extend(csv_reader.fieldnames)
            for csv_row in csv_reader:
                row = dict(csv_row)
                data = {}
                for attribute in row.keys():
                    if row[attribute]:
                        data.update({attribute: row[attribute]})
                    else:
                        if attribute not in attribute_fill:
                            attribute_fill.update(self._create_attribute_info(attribute))
                        if attribute_fill[attribute]['type'] == DataType.NUMERIC:
                            if numeric_fill == FillType.MEAN:
                                data.update({attribute: attribute_fill[attribute]['mean']})
                            elif numeric_fill == FillType.MEDIAN:
                                data.update({attribute: attribute_fill[attribute]['median']})
                            elif numeric_fill == FillType.MODE:
                                data.update({attribute: attribute_fill[attribute]['mode']})
                        elif attribute_fill[attribute]['type'] == DataType.CATEGORICAL:
                            data.update({attribute: attribute_fill[attribute]['mode']})
                        else:
                            data.update({attribute: fall_back})
                filled_data.append(data)

        if not file_name:
            file_name = self._file
        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(filled_data)

    def delete_missing_row(self, threshold: int = 1, threshold_pct: float = None, file_name: str = None) -> None:
        """
        Function deleting rows with missing values given a threshold

        ----

        Open the file to gather it's data and leave out rows that are not meet threshold condition

        |  If the number of missing attribute of current row bigger than this value, it will be deleted

        |  If threshold_pct is specified, the value in threshold will ne ignore.

        |  Filled data will be stored in a new data set and get saved with specified file name, if not specified, this
        new data will overwritten old data in old data file

        :param threshold: specified the limit that allow rows are kept from being deleted
        :param threshold_pct: specifies the percentage base on number of attribute this file has
        :param file_name: name of the file to save this data
        """
        missing_rows = self.missing_rows()
        new_data = []
        fieldnames = []

        if not file_name:
            file_name = self._file

        if threshold_pct:
            if threshold_pct < 0 or threshold_pct > 1:
                raise ValueError("Threshold_pct value must be between 0-1")
            else:
                with open(self._file, 'r') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
                    threshold = int(len(csv_reader.fieldnames) * threshold_pct)

        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            fieldnames.extend(csv_reader.fieldnames)
            for row_number, csv_row in enumerate(csv_reader):
                if row_number in missing_rows and len(missing_rows[row_number]) >= threshold:
                    continue
                new_data.append(csv_row)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)

    def delete_missing_column(self, threshold: int = 1, threshold_pct: float = None, file_name: str = None) -> None:
        """
        Function deleting attributes with missing rows, given a threshold

        ----

        Open the file to gather it's data and leave out attributes that are not meet threshold condition

        |   If the number of missing rows of current attribute bigger than this value, it will be deleted

        |  If threshold_pct is specified, the value in threshold will ne ignore.

        |  Filled data will be stored in a new data set and get saved with specified file name, if not specified
        this new data will overwritten old data in old data file

        :param threshold: specified the limit that allow attributes are kept from being deleted
        :param threshold_pct: specifies the percentage base on number of rows this file has
        :param file_name: name of the file to save this data
        """
        missing_cols = self.missing_cols()
        new_data = []
        fieldnames = []

        if not file_name:
            file_name = self._file

        if threshold_pct:
            if threshold_pct < 0 or threshold_pct > 1:
                raise ValueError("Threshold_pct value must be between 0-1")
            else:
                with open(self._file, 'r') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
                    row_count = sum(1 for _ in csv_reader)
                    threshold = int(row_count * threshold_pct)

        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            for csv_row in csv_reader:
                row = dict(csv_row)
                data = {}
                for attribute in row:
                    if attribute in missing_cols and len(missing_cols[attribute]) >= threshold:
                        continue
                    if attribute not in fieldnames:
                        fieldnames.append(attribute)
                    data.update({attribute: row[attribute]})
                new_data.append(data)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)

    def delete_duplicate_row(self, file_name: str = None) -> None:
        """
        Function to delete duplicated rows

        ----

        Open file and gather all data, perform duplication removal and store new data into new file

        |  If file name is not specified, the data will be saved on the old file

        :param file_name: name of the file to save this data
        """
        fieldnames = []
        if not file_name:
            file_name = self._file
        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=self._delimiter)
            fieldnames.extend(csv_reader.fieldnames)
            new_data = list(map(dict, set(tuple(sorted(csv_row.items())) for csv_row in csv_reader)))

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)

    def normalization(self, attribute: str, normalization_type: NormalizationType, file_name: str = None) -> None:
        """
        Function to perform normalization on a given NUMERIC attribute

        ----

        Only operate on NUMERIC data type and will raise error if the data type is different

        |  Deter which normalization type is specified then call suitable function, the returned data will then be saved
        to a new file

        |  If the name of the new file is not specified, the data will be saved on the old file

        :param attribute: name of the attribute
        :param normalization_type: may be of type z-score or min-max
        :param file_name: name of the file to save this data
        :raise: TypeError if data type of given attribute is not NUMERIC
        """
        if not file_name:
            file_name = self._file

        if self._deter_data_type(attribute) != DataType.NUMERIC:
            raise TypeError(f"Attribute is not of type {DataType.NUMERIC.name}")

        if normalization_type == NormalizationType.MIN_MAX:
            new_data, fieldnames = self._min_max(attribute)
        else:
            new_data, fieldnames = self._z_score(attribute)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)

    @staticmethod
    def do_calc_sub(operand_a: float, operand_b: float, name: str) -> Optional[float]:
        """
        A simple lookup table that operate requested operation on 2 operand

        :param operand_a: value 1
        :param operand_b: value 2
        :param name: of the expression, must be one of ['+', '-', '*', '/']
        :return: result of such operation
        :raises: NotImplementedError if operation is not supported (not in +, - , * , /)
        """
        if name == '+':
            return operand_a + operand_b
        elif name == '-':
            return operand_a - operand_b
        elif name == '*':
            return operand_a * operand_b
        elif name == '/':
            try:
                return operand_a / operand_b
            except ZeroDivisionError:
                return None
        else:
            raise NotImplemented(f"Operation '{name}' not supported")

    @staticmethod
    def do_calc(operations: list, data: dict) -> Optional[float]:
        """
        Function to perform calculation on NUMERIC attributes that has been turned to post-fix representation

        :param operations: post-fix form of the operation expression
        :param data: key-value pair of attributes and their values in specified row
        :return:
                float: value of this calculation,
                None: if one of values missing data
        :raise: Attribute error if no such attribute name in the data
        """
        to_cal = []
        for item in operations:
            if type_of(item) == EquationType.OPERATOR:
                to_cal.append(item)
            else:
                try:
                    if data[item] == '':
                        return None
                    try:
                        to_cal.append(float(data[item]))
                    except ValueError:
                        raise f"Data type is not {DataType.NUMERIC.name}"
                except KeyError as e:
                    raise AttributeError("No such attribute") from e
        for index, item in enumerate(to_cal):
            if type_of(item) == EquationType.OPERATOR:
                to_cal[index] = DataPreprocessor.do_calc_sub(to_cal[index - 2], to_cal[index - 1], to_cal[index])
        return to_cal[-1]

    def attributes_calculation(self, calc_str: str, col_name: str = None, file_name: str = None) -> None:
        """
        Function that do attribute calculation given an in-fix expression representation

        ----

        Open file to gather data, at each row, new column will be added which hold the results of calculated expression,
        then the new data, with an extra column will be saved to a new file

        |  If col name is not specified, it will be set to be the calc_str value

        | if file name is not specified ,the data will be saved on the old file

        :param calc_str: infix form of operation calculation
        :param col_name: name of the new column to output result
        :param file_name:  name of the file to save this data
        """
        operations = infix_to_postfix(calc_str)
        new_data = []
        fieldnames = []
        if not file_name:
            file_name = self._file
        if not col_name:
            calc_str = calc_str.replace(' ', '')
            col_name = ''.join(calc_str)

        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            fieldnames.extend(csv_reader.fieldnames)
            fieldnames.append(col_name)
            for csv_row in csv_reader:
                row = dict(csv_row)
                calc_result = DataPreprocessor.do_calc(operations, row)
                if calc_result is not None:
                    row[col_name] = calc_result
                else:
                    row[col_name] = ''
                new_data.append(row)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)
