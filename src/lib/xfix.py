import re
from stack import Stack
from enum import Enum
from typing import *


class EquationType(Enum):
    """
    Enum class define the type of string in an operation

    ----

    This class define 4 level of type of each string will be, which is:
        - left_parentheses: (
        - right_parentheses: )
        - operator: +, - ,*, / (only currently support these operator in calculation)

    """
    LEFT_PARENTHESES = 0
    RIGHT_PARENTHESES = 1
    OPERATOR = 2
    OPERAND = 3


# define operator dictionary to look up

operator = {
    "+": {
        "name": "add",
        "precede": 2,
    },
    "-": {
        "name": "sub",
        "precede": 2,
    },
    "*": {
        "name": "mul",
        "precede": 3,
    },
    "/": {
        "name": "div",
        "precede": 3,
    },
    "(": {
        "name": "lp",
        "precede": 1,
    },
    ")": {
        "name": "rp",
        "precede": 1,
    }
}


def parse_infix(infix_seq: str) -> List:
    """
    Function to split a string of expression to separate operand and operator, currently only works on +, - , *, /, (, )

    ----

    Use ``regEx`` library to split the input string based on an regular expression, this function return a list where
    each element is an operand or operator of the input mathematics expression, '(' and ')' included, along with 4
    expression: '+', '-', '*', '/'

    :param infix_seq: an operation expression, contain equation which need to be split
    :return: split items
    """
    r = re.compile(r'(?<=[-+*/\\(\\)])|(?=[-+*/\\(\\)])')
    redundancies = ['', ' ']
    items = r.split(infix_seq)
    items = list(filter(lambda a: a not in redundancies, items))
    items = [item.strip() for item in items]
    return items


def type_of(op_str: str) -> EquationType:
    """
    Function to determine which type of EquationType of this string

    ----

    With the pre-defined enum class EquationType, this function determine the type of input string, which can be 1 of 4 type:
        - LEFT_PARENTHESES
        - RIGHT_PARENTHESES
        - OPERATOR
        - OPERAND

    :param op_str: input string to determine type
    :return: defined type of this string
    """
    if op_str == '(':
        return EquationType.LEFT_PARENTHESES
    elif op_str == ')':
        return EquationType.RIGHT_PARENTHESES
    elif op_str in operator:
        return EquationType.OPERATOR
    else:
        return EquationType.OPERAND


def infix_to_postfix(infix_seq: str) -> List:
    """
    Turn a math expression to post-fix convention, only support +, -, *, / , (, ) at the moment

    ----

    Use infix-to-post-fix algorithm to turn an string of infix expression to post-fix. Steps can be describe as follow:
        1. Parse input string to get list contain separated operand and operand (parenthesis included)
        2. Use algorithm to re-arrange that list to a list follow post-fix convention


    :param infix_seq: input expression
    :return: a list of element follow the post-fix convention
    """
    infix_stack = parse_infix(infix_seq)
    output_stack = Stack()
    operator_stack = Stack()
    for item in infix_stack:
        if type_of(item) == EquationType.OPERAND:
            output_stack.push(item)
        else:
            if type_of(item) == EquationType.OPERATOR:
                while not operator_stack.is_empty() and operator[item]['precede'] < operator[operator_stack.top()][
                    'precede']:
                    output_stack.push(operator_stack.pop())
                operator_stack.push(item)
            elif type_of(item) == EquationType.LEFT_PARENTHESES:
                operator_stack.push(item)
            elif type_of(item) == EquationType.RIGHT_PARENTHESES:
                while not operator_stack.is_empty() and type_of(operator_stack.top()) != EquationType.LEFT_PARENTHESES:
                    output_stack.push(operator_stack.pop())
                operator_stack.pop()
    while not operator_stack.is_empty():
        output_stack.push(operator_stack.pop())
    return output_stack.items()
