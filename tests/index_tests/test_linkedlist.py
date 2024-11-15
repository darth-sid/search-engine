import unittest
from indexer.linkedlist import SortedLinkedList

class TestLinkedList(unittest.TestCase):
    def test_insert(self):
        llist = SortedLinkedList()
        llist.insert(1)
        llist.insert(4)
        llist.insert(3)
        llist.insert(-2)
        llist.insert(5)
        llist.insert(0)
        assert(list(llist) == [5,4,3,1,0,-2])

    def test_insert_dup(self):
        llist = SortedLinkedList()
        llist.insert(1)
        llist.insert(0)
        llist.insert(1)
        assert(list(llist) == [1,1,0])

    def test_delete(self):
        llist = SortedLinkedList()
        llist.insert(1)
        llist.insert(3)
        llist.insert(2)
        llist.remove(3)
        llist.insert(4)
        llist.remove(2)
        assert(list(llist) == [4,1])

    def test_delete_nonexistent(self):
        llist = SortedLinkedList()
        llist.insert(1)
        llist.insert(2)
        llist.insert(3)
        llist.remove(4)
        assert(list(llist) == [3,2,1])

    def test_empty(self):
        llist = SortedLinkedList()
        assert(list(llist) == [])

    def test_construct_from_list(self):
        llist = SortedLinkedList([4,1,3,2])
        assert(list(llist) == [4,3,2,1])
