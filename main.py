import math
import sys
import os
import argparse
import csv
from enum import Enum
from typing import Optional
from xfix import EquationType, infix_to_postfix, type_of


class FillType(Enum):
    MEAN = 0
    MEDIAN = 1
    MODE = 2


class NormalizationType(Enum):
    MIN_MAX = 0
    Z_SCORE = 1


class DataType(Enum):
    NUMERIC = 0
    CATEGORICAL = 1
    UNKNOWN = 2


class DataPreprocessor:
    def __init__(self, file: str, delimiter: str = ','):
        if os.path.isfile(file):
            self._file = file
            self._delimiter = delimiter
        else:
            raise FileNotFoundError(f"The file '{file}' can't be found, please try again")

    def missing_cols(self) -> dict:
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

    def missing_rows(self):
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

    def _deter_data_type(self, attribute: str) -> DataType:
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
                    print('yes')
                    raise AttributeError(f"No such attribute: {attribute}") from e
        return DataType.UNKNOWN

    def _standard_deviation(self, attribute: str):
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

        if has_value == 1:
            return 0
        return math.sqrt(total / (has_value - 1))

    def _mean(self, attribute: str) -> Optional[float]:
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

    def _mode(self, attribute: str) -> Optional[str]:
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

    def _create_attribute_info(self, attribute, fall_back=''):
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

    def _z_score(self, attribute: str):
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

    def _min_max(self, attribute: str):
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

    def fill_nan(self, numeric_fill: FillType, fall_back='0', file_name=''):
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

    def delete_missing_row(self, threshold: int = 1, threshold_pct: float = None, file_name: str = None):
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
                if row_number in missing_rows and len(missing_rows[row_number]) > threshold:
                    continue
                new_data.append(csv_row)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writerows(new_data)

    def delete_missing_column(self, threshold: int = 1, threshold_pct: float = None, file_name: str = None):

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
                    if attribute in missing_cols and len(missing_cols[attribute]) > threshold:
                        continue
                    if attribute not in fieldnames:
                        fieldnames.append(attribute)
                    data.update({attribute: row[attribute]})
                new_data.append(data)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)

    def delete_duplicate_row(self, file_name: str = None):
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

    def normalization(self, attribute: str, normalization_type: NormalizationType, file_name: str = None):
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
    def _do_calc_sub(operand_a, operand_b, name):
        if name == '+':
            return operand_a + operand_b
        elif name == '-':
            return operand_a - operand_b
        elif name == '*':
            return operand_a * operand_b
        elif name == '/':
            return operand_a / operand_b

    @staticmethod
    def _do_calc(operations, data):
        to_cal = []
        for item in operations:
            if type_of(item) == EquationType.OPERATOR:
                to_cal.append(item)
            else:
                try:
                    if data[item] == '':
                        return ''
                    to_cal.append(float(data[item]))
                except KeyError as e:
                    raise AttributeError("No such attribute") from e
        for index, item in enumerate(to_cal):
            if type_of(item) == EquationType.OPERATOR:
                to_cal[index] = DataPreprocessor._do_calc_sub(to_cal[index - 2], to_cal[index - 1], to_cal[index])
        return to_cal[-1]

    def attributes_calculation(self, calc_str, col_name, file_name: str = None):
        operations = infix_to_postfix(calc_str)
        new_data = []
        fieldnames = []
        if not file_name:
            file_name = self._file

        with open(self._file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            fieldnames.extend(csv_reader.fieldnames)
            fieldnames.append(col_name)
            for csv_row in csv_reader:
                row = dict(csv_row)
                row[col_name] = DataPreprocessor._do_calc(operations, row)
                new_data.append(row)

        with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_data)


if __name__ == '__main__':
    house_data = DataPreprocessor('house-prices.csv')
    house_data.attributes_calculation("a+b", "sup")
