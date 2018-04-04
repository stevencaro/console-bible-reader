from lxml import etree
from collections import OrderedDict
import pdb

class Bible:

    def __init__(self):
        #print('#### make a Bible')
        self.totalbooks = 0

    def __getattr__(self,name):
        #print('Setting ', name)
        super().__setattr__(name, Book(name))
        self.totalbooks += 1
        return getattr(self,name)

    def __call__(self, bk, ch):
        try:
            return getattr(self, bk).chaplist[ch]
        except AttributeError:
            errmsg = 'Book "{}" not found'.format(bk)
        except IndexError:
            errmsg = 'Chapter {} not found'.format(ch)
        else:
            raise DataError(errmsg)

    def __getstate__(self): return self.__dict__        # for pickling
    def __setstate__(self, d): self.__dict__.update(d)

class Book:

    def __init__(self, name):
        #print('  #### make a Book', name)
        try:
            self.name = FullName[name]
        except KeyError:
            self.name = name

        self.chaplist = [None]

    def add(self, ch, v, txt):
        try:
            chap = self.chaplist[ch]
        except IndexError:
            chap = Chapter(ch)
            self.chaplist.insert(ch, chap)
        chap.add(v, txt)

class Chapter:

    def __init__(self,ch):
        #print('    #### make a Chapter', ch)
        self.number = ch
        self.verslist = [None]

    def add(self, v, txt):
        self.verslist.insert(v, (str(v), txt)) ## FIX?

    def __getitem__(self, index):
        try:
            return self.verslist[index]
        except IndexError:
            errmsg = 'Verses {} not found'.format(ch)
        else:
            raise DataError(errmsg)


class BibleFromTextFile(Bible):

    def __init__(self, filename):
        super().__init__()

        with open(filename) as file:
            for line in file.readlines():
                bk,ch,v,txt = line.split('|')
                bk  = bk.lower()
                txt = txt.rstrip().lstrip()#  .capitalize()  FIX: ??
                txt = txt.rstrip('~')
                book = getattr(self,bk)
                book.add(int(ch),int(v),txt)


class ReinaValeraBible(BibleFromTextFile):

    def __init__(self):
        self.title = "Reina Valera"
        filename = 'data/esrv.txt'
        super().__init__(filename)


class KingJamesBible(BibleFromTextFile):

    def __init__(self):
        self.title = "King James"
        filename = 'data/kjvdat.txt'
        super().__init__(filename)


class VulgateBible(BibleFromTextFile):

    def __init__(self):
        self.title = "Vulgate"
        filename = 'data/vulgate.txt'
        super().__init__(filename)


class BibleFromNeoVulgateXMLFiles(Bible):

    def __getattribute__(self,name):
        transtable = {'exo':'ex', 'rev':'ap', 'luk':'lc', 'psa':'ps',  'pro':'prov', 'mat':'mt',
                      'mar':'mc', 'joh':'io', 'eze':'ez', 'ecc':'qoh', 'job':'iob',  'heb': 'hebr',
                      'deu':'deut' }
        if name in transtable.keys():
            transname = transtable[name]
            return Bible.__getattribute__(self,transname)
        else:
            return Bible.__getattribute__(self,name)

    def __init__(self):
        super().__init__()
        datadir = 'data/neovulgate/'
        table = str.maketrans({'æ':'ae', 'œ':'oe', '\u00a0':' ', 'Æ':'Ae', '\n': ' '})
        files = ['1chr.xml', '1cor.xml', '1io.xml', '1mac.xml', '1petr.xml', '1reg.xml',
                '1sam.xml', '1th.xml', '1tim.xml', '2chr.xml', '2cor.xml',
                '2io.xml', '2mac.xml', '2petr.xml', '2reg.xml', '2sam.xml',
                '2th.xml', '2tim.xml', '3io.xml', 'abd.xml', 'act.xml',
                'ag.xml', 'am.xml', 'ap.xml', 'bar.xml', 'cant.xml', 'col.xml',
                'dan.xml', 'deut.xml', 'eph.xml', 'esd.xml', 'est.xml',
                'ex.xml', 'ez.xml', 'gal.xml', 'gen.xml', 'hab.xml',
                'hebr.xml', 'iac.xml', 'ier.xml', 'iob.xml', 'ioel.xml',
                'ion.xml', 'ios.xml', 'io.xml', 'is.xml', 'iudic.xml',
                'iudt.xml', 'iud.xml', 'lam.xml', 'lc.xml', 'lev.xml',
                'mal.xml', 'mc.xml', 'mic.xml', 'mt.xml', 'nah.xml', 'neh.xml',
                'num.xml', 'os.xml', 'phil.xml', 'phm.xml', 'prov.xml',
                'ps.xml', 'qoh.xml', 'rom.xml', 'rut.xml', 'sap.xml',
                'sir.xml', 'soph.xml', 'tit.xml', 'tob.xml', 'zac.xml']

        for f in files:
            root = etree.parse(datadir + f).getroot()
            if root.attrib['elibro'].startswith(('1','2','3')):
                prefix = '_'
            else:
                prefix = ''
            title = prefix + root.attrib['elibro']

            for elem in root.getchildren():
                if elem.tag != 'cap': continue
                try:
                    cnum = int(elem.attrib['num']) or 1  # num == 0 in xml when only 1 chapter
                except KeyError:
                    cnum = 1

                vnumcorrection = 0
                for v in elem.getchildren():
                    #if v.tag != 'vers': continue

                    if v.find('cursiva') is not None: # strip <cursiva> tags in ps.xml
                        head = v.text
                        tail = v.find('cursiva').tail
                        v.remove(v.find('cursiva'))
                        v.text = (head + tail).lstrip(' .')

                    try:                             # scrubs cases like: <vers num="(34) 35"
                        vnum = int(v.attrib['num'])
                    except (KeyError, ValueError):
                        vnum = lastvnum + 1
                        lastvnum += 1
                    else:
                        lastvnum = vnum

                    txt = v.text.translate(table).strip()

                    if txt == '' or txt is None:
                        vnumcorrection = -1      # to adjust for deleted <cursiva> tags
                        continue

                    getattr(self,title).add(cnum, vnum + vnumcorrection, txt)


class BibleFromXMLFile(Bible):

    def __init__(self, filename):
        super().__init__()
        root = etree.parse(filename).getroot()
        books = root.getchildren()

        for elem in books:
            title = abbr4name(elem.attrib['name'])
            chapters = elem.getchildren()
            for elem in chapters:
                cnum = int(elem.attrib['name'])
                verses = elem.getchildren()
                for v in verses:
                    vnum = int(v.attrib['name'])
                    txt = v.text
                    getattr(self,title).add(cnum,vnum,txt)

class BibleFromXMLFileB(Bible):

    def __init__(self, filename):
        super().__init__()
        root = etree.parse(filename).getroot()
        books = root.getchildren()

        for elem in books:    ### 66 of <Element b at 0x7f0c90fba1c8>

            #title = ShortName[elem.attrib['c']]
            title = abbr4name(elem.attrib['n'])

            chapters = elem.getchildren()
            for elem in chapters: ###        <Element c at 0x7f0c91630c88>,

                #pdb.set_trace()
                cnum = int(elem.attrib['n'])
                verses = elem.getchildren()

                for v in verses:
                    vnum = int(v.attrib['n'])
                    txt = v.text
                    #print(txt)
                    getattr(self,title).add(cnum,vnum,txt)

class BibleFromXMLFileC(Bible):

    def __init__(self, filename):
        super().__init__()
        root = etree.parse(filename).getroot()
        books = root.getchildren()
        books.pop(0)
        for elem in books:    ### 66 of <Element b at 0x7f0c90fba1c8>

            #title = ShortName[elem.attrib['b']]
            title = abbr4name(elem.attrib['bname'])

            chapters = elem.getchildren()
            for elem in chapters: ###        <Element c at 0x7f0c91630c88>,

                #pdb.set_trace()
                cnum = int(elem.attrib['cnumber'])
                verses = elem.getchildren()

                for v in verses:
                    vnum = int(v.attrib['vnumber'])
                    txt = v.text
                    #print(txt)
                    getattr(self,title).add(cnum,vnum,txt)


class NeoVulgateBible(BibleFromNeoVulgateXMLFiles):

    def __init__(self):
        self.title = "Neo Vulgate"
        super().__init__()

class LutherBible(BibleFromXMLFileC):

    def __init__(self):
        self.title = "Luther"
        filename = 'data/luther.xml'
        super().__init__(filename)


class NeuvaVersionInternacionalBible(BibleFromXMLFileB):

    def __init__(self):
        self.title = "New International Spanish"
        filename = 'data/nvi-es.xml'
        super().__init__(filename)
class NewInternationalBible(BibleFromXMLFile):

    def __init__(self):
        self.title = "New International"
        filename = 'data/niv.xml'
        super().__init__(filename)


class NewKingJamesBible(BibleFromXMLFile):

    def __init__(self):
        self.title = "New King James"
        filename = 'data/nkjv.xml'
        super().__init__(filename)


class DataError(Exception):
    pass

abbrlist = [
    (['Genesis',         "Génesis",          '1 Mose'           ], "gen"),
    (['Exodus',          "Éxodo",            '2 Mose'           ], "exo"),
    (['Leviticus',       "Levitico",         '3 Mose'           ], "lev"),
    (['Numbers',         "Números",          '4 Mose'           ], "num"),
    (['Deuteronomy',     "Deuteronomio",     '5 Mose'           ], "deu"),
    (['Joshua',          "Josué",            'Josua'            ], "jos"),
    (['Judges',          "Jueces",           'Richter'          ], "jdg"),
    (['Ruth',            "Rut",              'Rut'              ], "rut"),
    (['1 Samuel',        "1 Samuel",         '1 Samuel'         ], "sa1"),
    (['2 Samuel',        "2 Samuel",         '2 Samuel'         ], "sa2"),
    (['1 Kings',         "1 Reyes",          '1 Könige'         ], "kg1"),
    (['2 Kings',         "2 Reyes",          '2 Könige'         ], "kg2"),
    (['1 Chronicles',    "1 Crónicas",       '1 Chronik'        ], "ch1"),
    (['2 Chronicles',    "2 Crónicas",       '2 Chronik'        ], "ch2"),
    (['Ezra',            "Esdras",           'Esra'             ], "ezr"),
    (['Nehemiah',        "Nehemías",         'Nehemia'          ], "neh"),
    (['Esther',          "Ester",            'Ester'            ], "est"),
    (['Job',             "Job",              'Hiob'             ], "job"),
    (['Psalms',          "Salmos",           'Psalm'            ], "psa"),
    (['Proverbs',        "Proverbios",       'Sprüche'          ], "pro"),
    (['Ecclesiastes',    "Eclesiastés",      'Prediger'         ], "ecc"),
    (['Song of Solomon', "Cantares",         'Hohelied'         ], "sol"),
    (['Isaiah',          "Isaías",           'Jesaja'           ], "isa"),
    (['Jeremiah',        "Jeremías",         'Jeremia'          ], "jer"),
    (['Lamentations',    "Lamentaciones",    'Klagelieder'      ], "lam"),
    (['Ezekiel',         "Ezequiel",         'Hesekiel'         ], "eze"),
    (['Daniel',          "Daniel",           'Daniel'           ], "dan"),
    (['Hosea',           "Oseas",            'Hosea'            ], "hos"),
    (['Joel',            "Joel",             'Joel'             ], "joe"),
    (['Amos',            "Amós",             'Amos'             ], "amo"),
    (['Obadiah',         "Abdías",           'Obadja'           ], "oba"),
    (['Jonah',           "Jonás",            'Jona'             ], "jon"),
    (['Micah',           "Miqueas",          'Micha'            ], "mic"),
    (['Nahum',           "Nahúm",            'Nahum'            ], "nah"),
    (['Habakkuk',        "Habacuc",          'Habakuk'          ], "hab"),
    (['Zephaniah',       "Sofonías",         'Zephanja'         ], "zep"),
    (['Haggai',          "Hageo",            'Haggai'           ], "hag"),
    (['Zechariah',       "Zacarías",         'Sacharja'         ], "zac"),
    (['Malachi',         "Malaquías",        'Maleachi'         ], "mal"),
    (['Matthew',         "Mateo",            'Matthäus'         ], "mat"),
    (['Mark',            "Marcos",           'Markus'           ], "mar"),
    (['Luke',            "Lucas",            'Lukas'            ], "luk"),
    (['John',            "Juan",             'Johannes'         ], "joh"),
    (['Acts',            "Hechos",           'Apostelgeschichte'], "act"),
    (['Romans',          "Romanos",          'Römer'            ], "rom"),
    (['1 Corinthians',   "1 Corintios",      '1 Korinther'      ], "co1"),
    (['2 Corinthians',   "2 Corintios",      '1 Korinther'      ], "co2"),
    (['Galatians',       "Gálatas",          'Galater'          ], "gal"),
    (['Ephesians',       "Efesios",          'Epheser'          ], "eph"),
    (['Philippians',     "Filipenses",       'Philipper'        ], "phi"),
    (['Colossians',      "Colosenses",       'Kolosser'         ], "col"),
    (['1 Thessalonians', "1 Tesalonicenses", '1 Thessalonicher' ], "th1"),
    (['2 Thessalonians', "2 Tesalonicenses", '2 Thessalonicher' ], "th2"),
    (['1 Timothy',       "1 Timoteo",        '1 Timotheus'      ], "ti1"),
    (['2 Timothy',       "2 Timoteo",        '2 Timotheus'      ], "ti2"),
    (['Titus',           "Tito",             'Titus'            ], "tit"),
    (['Philemon',        "Filemón",          'Philemon'         ], "plm"),
    (['Hebrews',         "Hebreos",          'Hebräer'          ], "heb"),
    (['James',           "Santiago",         'Jakobus'          ], "jam"),
    (['1 Peter',         "1 Pedro",          '1 Petrus'         ], "pe1"),
    (['2 Peter',         "2 Pedro",          '2 Petrus'         ], "pe2"),
    (['1 John',          "1 Juan",           '1 Johannes'       ], "jo1"),
    (['2 John',          "2 Juan",           '2 Johannes'       ], "jo2"),
    (['3 John',          "3 Juan",           '3 Johannes'       ], "jo3"),
    (['Jude',            "Judas",            'Judas'            ], "jde"),
    (['Revelation',      "Apocalipsis",      'Offenbarung'      ], "rev")

]

def abbr4name(name):

    for names,abbr in abbrlist:
        if name in names:
            return abbr
    return name

#LongName = OrderedDict()
#ShortName = OrderedDict()

#for b in books:              # refactor to use abbrlist
#    longname, abbr = b
#    LongName[abbr] = longname
#    ShortName[longname] = abbr

FullName = OrderedDict()
#AbbrName = OrderedDict()

for names,abbr in abbrlist:
    fullname = names[0]
    FullName[abbr] = fullname
#    AbbrName[fullname] = abbr


