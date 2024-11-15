class Node:
    def __init__(self, val):
        self.val = val
        self.next = None 

class SortedLinkedList:
    def __init__(self, from_list=None):
        self.head = Node(None)
        self.head.next = Node(None)
        if from_list is not None:
            for val in from_list:
                self.insert(val)

    def __iter__(self):
        curr = self.head.next
        while curr.val is not None:
            yield curr.val
            curr = curr.next

    def __add__(self, other):
        return self

    def insert(self, val):
        prev_node = self.head
        next_node = self.head.next

        while (next_node.val is not None and next_node.val > val):
            prev_node = next_node
            next_node = next_node.next

        new_node = Node(val)
        prev_node.next = new_node
        new_node.next = next_node

    def remove(self, val):
        if val is None:
            return
        prev_node = self.head
        curr_node = self.head.next
        while curr_node.val is not None and curr_node.val > val:
            prev_node = curr_node
            curr_node = curr_node.next
        if curr_node.val == val:
            prev_node.next = curr_node.next
