#!/usr/bin/python3

from model import *
import pickle

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]

class BibleVersion(object):                          # dictionary-like singleton
    __metaclass__ = Singleton

    def __init__(self):

        self.pickles =  {
                         'kj'  : 'data/kjv.pickle',
                         'vulg': 'data/vulg.pickle',
                         'niv' : 'data/niv.pickle',
                         'nkj' : 'data/nkj.pickle',
                         'nvi' : 'data/nvi-es.pickle',
                         'nv'  : 'data/nv.pickle',   # 10 loops, best of 3: 51.7 ms per loop
                         'lu'  : 'data/lut.pickle' } # 10 loops, best of 3: 53.5 ms per loop

        self.versions = self.pickles.keys()

    def __call__(self, key):
        try:
            if isinstance(self.pickles[key], str):
                with open(self.pickles[key], 'br') as data:
                    self.pickles[key] = pickle.load(data)
        except TypeError:
            pass

        return self.pickles[key]

