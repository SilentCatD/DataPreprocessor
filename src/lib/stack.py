from typing import *


class Stack:
    """
    A simple implementation of Stack data structure
    """

    def __init__(self, items: list = None) -> None:

        """
        Class constructor

        ----

        Copy item from list items parameter into the stack's item list, if there are not any item in this parameter or
        if there are no list passed as an argument, this stack will be initialized as an empty stack

        :param items:  a 1D iterable, the items of this iterable will be initialize in the stack, if not specified,
                    the stack will be empty
        """
        self._item = []
        if items:
            self._item = [item for item in items]

    def push(self, item: Any) -> None:
        """
        Push item into the top of the stack

        :param item: item to push
        """
        self._item.append(item)

    def pop(self) -> Optional[Any]:
        """
        Pop item from the top of the stack an return it, this DOES affect the stack's items list

        :return:
            Top most <item> of the stack if stack is not empty
            <None> if stack is empty
        """
        if not self.is_empty():
            return self._item.pop()
        return None

    def is_empty(self) -> int:
        """
        Determine whether the stack is empty or not

        :return: <boolean> value represent if the stack is empty
        """
        return len(self._item) == 0

    def size(self) -> int:
        """
        Determine the size of the stack

        :return: <int> value represent the size of the stack
        """
        return len(self._item)

    def top(self) -> Any:
        """
        Get the top most item of the stack then return it, this does NOT affect the stack's item list

        :return: Top most <item> of the stack
        """
        if not self.is_empty():
            return self._item[-1]
        return None

    def items(self) -> List:
        """
        Get the copy of the current stack items

        :return: <List> copy of all <item> in stack
        """
        return self._item[:]
