#!/usr/bin/env python2
# coding: utf-8

class MinPriorityQueue(object):
    """
    Maintain a structure that pops out the smallest one.
    Currently the internal structure is only a list
    """
    def __init__(self, sortkey=None):
        self.sort_ = lambda x: sortkey(x) if sortkey is not None else x
        self.data_ = []

    def insert(self, key):
        self.data_.append(key)

    def pop(self):
        minpos = None
        minkey = None
        for i, x in enumerate(self.data_):
            if minkey is None or self.sort_(x) < self.sort_(minkey):
                minpos, minkey = i, x

        if minkey is None:
            raise ValueError('failed to pop out an empty queue')

        self.data_ = self.data_[:minpos] + self.data_[minpos + 1:]
        return minkey

if __name__ == "__main__":
    pq = MinPriorityQueue()
    pq.insert(1)
    pq.insert(2)
    pq.insert(3)
    pq.insert(4)
    pq.insert(5)
    print "following should be 1 2 3 4"
    print pq.pop(), pq.pop(), pq.pop(), pq.pop()

    pq.insert(3)
    pq.insert(4)
    pq.insert(1)
    print "following should be 1 3 4 5"
    print pq.pop(), pq.pop(), pq.pop(), pq.pop()

    pq = MinPriorityQueue(lambda x: -x)
    pq.insert(1)
    pq.insert(2)
    pq.insert(3)
    pq.insert(4)
    pq.insert(5)
    print "following should be 5 4 3 2"
    print pq.pop(), pq.pop(), pq.pop(), pq.pop()

    pq.insert(3)
    pq.insert(4)
    pq.insert(1)
    print "following should be 4 3 1 1"
    print pq.pop(), pq.pop(), pq.pop(), pq.pop()

