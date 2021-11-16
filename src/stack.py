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

        ----

        Item in param will be appended in the list of this stack

        :param item: item to push
        """
        self._item.append(item)

    def pop(self) -> Optional[Any]:
        """
        Pop item from the top of the stack an return it

        ----

        Remove the top  most item in the stack, which will affect the stack's list of items and return it, in case the
        stack is empty, this function will return None

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

        ----

        Use the len of the item list of this stack to determine if the stack is empty,
        then return a boolean value accordingly

        :return: <boolean> value represent if the stack is empty
        """
        return len(self._item) == 0

    def size(self) -> int:
        """
        Determine the size of the stack

        ----

        Calculate the len of the list of this stack then return that len

        :return: <int> value represent the size of the stack
        """
        return len(self._item)

    def top(self) -> Any:
        """
        Get the top most item of the stack then return it

        ----

        This does not affect items in the stack, if the stack is empty, this will return None

        :return: Top most <item> of the stack
        """
        if not self.is_empty():
            return self._item[-1]
        return None

    def items(self) -> List:
        """
        Get the copy of the current stack items

        ----

        Copy the item list of this stack in a new list and return it

        :return: <List> copy of all <item> in stack
        """
        return self._item[:]
