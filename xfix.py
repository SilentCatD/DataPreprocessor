import re
from stack import Stack
from enum import Enum


class EquationType(Enum):
    LEFT_PARENTHESES = 0
    RIGHT_PARENTHESES = 1
    OPERATOR = 2
    OPERAND = 3


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


def parse_infix(infix_seq):
    r = re.compile(r'(?<=[-+*/\\(\\)])|(?=[-+*/\\(\\)])')
    redundancies = ['', ' ']
    items = r.split(infix_seq)
    items = list(filter(lambda a: a not in redundancies, items))
    items = [item.strip() for item in items]
    return items


def type_of(op_str):
    if op_str == '(':
        return EquationType.LEFT_PARENTHESES
    elif op_str == ')':
        return EquationType.RIGHT_PARENTHESES
    elif op_str in operator:
        return EquationType.OPERATOR
    else:
        return EquationType.OPERAND


def infix_to_postfix(infix_seq):
    infix_stack = parse_infix(infix_seq)
    output_stack = Stack()
    operator_stack = Stack()
    for item in infix_stack:
        if type_of(item) == EquationType.OPERAND:
            output_stack.push(item)
        else:
            if type_of(item) == EquationType.OPERATOR:
                while not operator_stack.is_empty() and operator[item]['precede'] < operator[operator_stack.top()]['precede']:
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


def operate(operand_a, operand_b, name):
    if name == '+':
        return operand_a + operand_b
    elif name == '-':
        return operand_a - operand_b
    elif name == '*':
        return operand_a * operand_b
    elif name == '/':
        return operand_a / operand_b




# result = calculate(infix_to_postfix(string), data_dict)
