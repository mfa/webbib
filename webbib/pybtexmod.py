# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012 by Andreas Madsack.

"""
from os import path
from pybtex import auxfile
from pybtex.plugin import find_plugin

from pybtex.style import FormattedBibliography
from pybtex.style.template import FieldIsMissing

from pybtex.style.formatting.unsrt import Style
from pybtex.style import FormattedEntry

class MyAuxData(auxfile.AuxData):
    def parse_stream(self, auxdata):
        for command, value in self.command_re.findall(auxdata):
            self.handle(command, value)

def parse_auxfile_from_stream(auxdata, encoding):
    """Parse a stream and return an AuxData object."""

    data = MyAuxData(encoding)
    data.parse_stream(auxdata)
    if data.data is None:
        raise auxfile.AuxDataError(r'found no \bibdata command in stream')
    if data.style is None:
        raise auxfile.AuxDataError(r'found no \bibstyle command in stream')
    return data


class MyFormattedBibliography(FormattedBibliography):
    def __init__(self, entries, style):
        # FIXME: do sth. with the errors
        self.entries = []
        errors = []
        while True:
            try:
                elem = next(entries)
            except StopIteration:
                break
            if isinstance(elem, tuple) and isinstance(elem[0], Exception):
                errors.append(elem)
                continue
            self.entries.append(elem)
        self.style = style

class MyStyle(Style):

    def format_entries(self, entries):
        sorted_entries = self.sort(entries)
        for number, entry in enumerate(sorted_entries):
            entry.number = number + 1
            for persons in entry.persons.itervalues():
                for person in persons:
                    person.text = self.format_name(person, self.abbreviate_names)

            f = getattr(self, "format_" + entry.type)
            try:
                text = f(entry)
            except FieldIsMissing, e:
                yield (e, entry)
            label = self.format_label(entry)
            yield FormattedEntry(entry.key, text, label)


def render(bib_filename):

    aux_filename="IMSfull.aux"
    bib_format=None
    bib_encoding=None
    output_encoding=None
    output_backend='html'
    min_crossrefs=2
    kwargs = {}
    auxstring = """
\\relax 
\\citation{*}
\\bibstyle{unsrt}
\\bibdata{%s}
""" % bib_filename

    aux_data = parse_auxfile_from_stream(auxstring, output_encoding)
    output_backend = find_plugin('pybtex.backends', output_backend)
    bib_parser = find_plugin('pybtex.database.input', bib_format)
    bib_data = bib_parser(
        encoding=bib_encoding,
        wanted_entries=aux_data.citations,
        min_crossrefs=min_crossrefs,
        ).parse_files(aux_data.data, bib_parser.get_default_suffix())
    
    style = MyStyle(
        label_style=kwargs.get('label_style'),
        name_style=kwargs.get('name_style'),
        sorting_style=kwargs.get('sorting_style'),
        abbreviate_names=kwargs.get('abbreviate_names'),
        )
    citations = bib_data.add_extra_citations(aux_data.citations, min_crossrefs)
    entries = (bib_data.entries[key] for key in citations)
    formatted_entries = style.format_entries(entries)

    return MyFormattedBibliography(formatted_entries, style)
