class Stack:
    def __init__(self, items=None):
        self._item = []
        if items:
            self._item = [item for item in items]

    def push(self, item):
        self._item.append(item)

    def pop(self):
        if not self.is_empty():
            return self._item.pop()
        return None

    def is_empty(self):
        return len(self._item) == 0

    def size(self):
        return len(self._item)

    def top(self):
        if not self.is_empty():
            return self._item[-1]
        return None

    def items(self):
        return self._item[:]
