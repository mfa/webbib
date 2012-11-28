# -*- coding: utf-8 -*-
"""
:copyright: (c) 2010-2012 by Andreas Madsack.

"""

from lxml import etree
from pybtex.database.input import bibtex
from pybtex.database.output.bibtex import Writer
from pybtex.database import BibliographyData
import StringIO
import codecs
import sys
import os
import re

import simplejson
import hashlib

class Staff():

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        print "Load Staff"
        self.staff_filename = os.path.join(os.path.dirname(__file__), 
                                           self.filename)
        self.load_staff(filename=self.staff_filename)

    def check_if_changed(self):
        if os.path.getmtime(self.filename) > self.lastload:
            print "reload data - %s" % self.filename
            self.load_staff(filename=self.staff_filename)

    def load_staff(self, filename='staff.xml'):
        """returns dict of staff-members:
        lastname, firstname, current [True, False]
        """
        self.lastload = os.path.getmtime(filename)
        self.filename = filename
        f = codecs.open(filename, encoding='latin-1')
        contents = f.read()
        root = etree.fromstring(contents.encode('latin-1'))
        # authors aufsammeln:
        authors = {}
        shorten = {}
        for author in root.xpath('//authors/current/author'):
            a = self.add_author_to_dict(author, current=True)
            authors[(a.get('lastname'), a.get('firstname'))] = a
            shorten[(a.get('lastname'), a.get('firstname')[0]+'.')] = a
        for author in root.xpath('//authors/former/author'):
            a = self.add_author_to_dict(author, current=False)
            authors[(a.get('lastname'), a.get('firstname'))] = a
            shorten[(a.get('lastname'), a.get('firstname')[0]+'.')] = a
        f.close()
        # set at end -> less time for threading problems
        self.authors = authors
        self.shorten = shorten

    def author_is_staff(self, lastname, firstname):
        if (lastname, firstname) in self.authors:
            return self.authors[(lastname, firstname)]
        if (lastname, firstname) in self.shorten:
            return self.shorten[(lastname, firstname)]
        return None

    def add_author_to_dict(self, author, current=False):
        """adds an author (xml-entity) to the author dict
        no testing of author is already set!!
        """
        a = {}
        lastname = author.find('lastname').text
        firstname = author.find('firstname').text
        a['lastname'] = lastname
        a['firstname'] = firstname
        a['current'] = current
        return a

    def get_staff_list(self, current=True, sort_them=True):
        # alle rausfiltern, die current ensprechen
        result = filter(lambda x: x['current']==current, self.authors.values())
        if sort_them:
            return sorted(result, key=lambda x: x.get('lastname').lower())
        else:
            return result


class Bibliography:

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        print "Load Bibliography"
        self.clean_variables()
        # load bib-file (first time)
        self.bib_filename = os.path.join(os.path.dirname(__file__),
                                         self.filename)
        self.load_bib(filename=self.bib_filename)

    def check_if_changed(self):
        if os.path.getmtime(self.filename) > self.lastload:
            print "reload data - %s" % self.filename
            # clean xml-root and years-cache
            self.clean_variables()
            # load bib-file (after change)
            self.load_bib(filename=self.bib_filename)

    def clean_variables(self):
        # xml_root of document (lxml)
        self.xml_root = None
        # cache for list of possible years
        self.years = []

    def load_bib(self, filename='IMSfull.bib'):
        parser = bibtex.Parser()
        bib_data = parser.parse_file(filename)
        self.lastload = os.path.getmtime(filename)
        self.filename = filename
        pubs = []
        index_keys = {}
        for key, elem in bib_data.entries.iteritems():
            entry = elem.fields

            # generate original bibtex
            # using StringIO and bibtex.writer
            a = BibliographyData()
            a.add_entry(key, elem)
            output = StringIO.StringIO()
            w = Writer()
            w.write_stream(a, output)
            entry['bibtex'] = output.getvalue()

            # sha1 for absolute unique keys
            x = hashlib.sha1(simplejson.dumps(entry))
            entry['key'] = x.hexdigest()
            entry['authors'] = self.parse_authors(elem.persons)

            # keywords
            entry['keywords'] = []
            if entry.get('keyword'):
                for i in entry['keyword'].split(','):
                    entry['keywords'].append(i.strip())
            entry['reference'] = self.render_references(elem.type, entry)

            # append to pubs
            pubs.append(entry)
            index_keys[x.hexdigest()] = len(pubs) - 1
            if 'year' not in entry:
                entry['year'] = ''
        # set at end -> less time for threading problems
        self.index_keys = index_keys
        self.pubs = pubs

    def parse_authors(self, persons):
        authors = []
        todo = []
        if persons.get('author'):
            todo.extend(persons.get('author'))
        if persons.get('editors'):
            todo.extend(persons.get('editors'))
            
        for elem in todo:
            d = {}
            d['lastname'] = striptex(elem.last()[0])
            d['firstname'] = striptex(elem.first()[0])
            authors.append(d)
        return authors

    def render_references(self, typ, entry):
        # FIXME: use pybtex for this part
        if typ=='techreport':
            return "%s, %s" % (entry.get('type'), 
                               entry.get('institution'))
        if typ=='inproceedings':
            return "in %s, %s, %s" % (entry.get('booktitle'), 
                                      entry.get('pages'),
                                      entry.get('publisher'),
                                      )

    def get_author_as_stringXXX(self, author_list):
        """ aus der liste einen string machen

        falls nur ein element in der "liste", ist es keine liste, 
        sondern nur das dict mit lastname/firstname
        => falls keine liste, eine liste drumherum machen
        """
        def author(x):
            return "%s, %s" % (x.get('lastname'), x.get('firstname'))
        if not isinstance(author_list, list):
            raise TypeError, "author_list is no list!"
        if len(author_list) == 0:
            raise IndexError, "author_list is empty"
        if not isinstance(author_list[0], dict):
            raise TypeError, "first list element is no dict"
        return "; ".join(map(author, author_list))

    # search helpers

    def by_year_filter(self, elem, yearlist):
        if not isinstance(yearlist, list):
            yearlist = [str(yearlist)]
        if elem.get('year') in yearlist:
            return True
        return False

    def search_by_year(self, year, publist=None):
        if not publist:
            publist = self.pubs
        return [item for item in publist if self.by_year_filter(item, year)]

    def by_author_filter(self, elem, lastname, firstname):
        for e in elem['authors']:
            if e['lastname'].lower() == lastname.lower() \
                    and e['firstname'].lower() == firstname.lower():
                return True
            # compare only first character of firstname
            if e['lastname'].lower() == lastname.lower() \
                    and e['firstname'][0].lower() == firstname[0].lower():
                return True
        return False

    def search_by_author(self, lastname, firstname, publist=None):
        if not publist:
            publist = self.pubs
        return [item for item in publist if self.by_author_filter(item, 
                                                                  lastname, 
                                                                  firstname)]

    def search_by_title(self, title, publist=None):
        if not publist:
            publist = self.pubs
        return filter(lambda x:str(title).lower() in x.get('title').lower(),
                      publist)

    def by_keyword_filter(self, elem, keyword):
        for s in elem['keywords']:
            if s.lower() == keyword.lower():
                return True
        return False

    def search_by_keyword(self, keyword, publist=None):
        if not publist:
            publist = self.pubs
        return [item for item in publist if self.by_keyword_filter(item, 
                                                                   keyword)]

    def get_target_for_element(self, element_key):
        if element_key in self.index_keys:
            return self.pubs[self.index_keys[element_key]]
        else:
            return None

    def get_years_list(self):
        if not self.years:
            self.years = list(set(map(lambda x:x.get('year'), self.pubs)))
            self.years.sort(reverse=True)
        return self.years


def striptex(s):
    # replace all umlauts (hopefully) -- FIXME
    tbl = ((r'\\"{u}', u'ü'),
           (r'\\"u', u'ü'),
           (r'\\"{a}', u'ä'),
           (r'\\"a', u'ä'),
           (r'\\"{o}', u'ö'),
           (r'\\"o', u'ö'),
           )
    for i,j in tbl:
        s = re.sub(r'(%s)' % i, j, s)
    # replace all { and }
    s = re.sub(r'(\{|\})', "", s)
    return s
