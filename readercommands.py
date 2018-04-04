# coding: utf-8
from pyparsing import *

class ReaderCommands():
    '''Helper class that interprets commands for Reader class'''

    def __init__(self, reader):
        self.reader = reader
        self.validversions = self.reader.bible.versions

        # command tokens
        book    = Word( alphanums, min=3, max=4)('book')
        chapnum = Word( nums, max=3)('chap')
        side    = Word( 'lr', max=1)('side')
        version = Or(   [CaselessKeyword(word) for word in self.validversions] )('version')

        # command grammar
        load_ch      = (chapnum + StringEnd()).setParseAction(self.cmd1)
        load_book    = (book    + StringEnd()).setParseAction(self.cmd2)
        load_book_ch = (book    + chapnum    ).setParseAction(self.cmd3)
        load_version = (side    + version).setParseAction(self.cmd4)

        self.parsers = (load_ch, load_book, load_book_ch, load_version)

    def cmd1(self, _, __, res):
        ''' Loads chapter only'''
        self.reader.update(book = self.reader.currbook, chap = int(res.pop('chap')))

    def cmd2(self, _, __, res):        # consolidate with cmd3?
        ''' Loads book only'''
        self.reader.update(book = res.pop('book')) #, chap = self.reader.currchap)

    def cmd3(self, _, __, res):
        ''' Loads book and chapter'''
        self.reader.update (book = res.pop('book'), chap = int(res.pop('chap')))

    def cmd4(self, _, __, res):
        ''' Loads bible into left side or right side of reader'''
        side = res.pop('side')
        version = res.pop('version')

        if side == 'l':
            self.reader.lbible = self.reader.bible(version)
        elif side == 'r':
            self.reader.rbible = self.reader.bible(version)

        self.reader.update(self.reader.currbook, self.reader.currchap)

    def parse_command(self, cmd):

        for parser in self.parsers:
            try:
                res = parser.parseString(cmd)
                break
            except ParseException as e:
                continue

