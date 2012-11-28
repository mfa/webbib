# -*- coding: utf-8 -*-
#
# Webbib
#

"""
:copyright: (c) 2010-2012 by Andreas Madsack.

"""

from flask import Flask, render_template, url_for, request, Response
from flask import session, abort
from flaskext.babel import Babel, refresh, gettext

from lxml import etree
import codecs
import bibmod
import re

### globals

app = Flask(__name__)
babel = Babel(app)

# Config
app.config.from_object('config.ExampleConfig')

# global bib and staff
bib = bibmod.Bibliography(app.config.get('BIB_FILENAME'))
bib.load()
staff = bibmod.Staff(app.config.get('STAFF_FILENAME'))
staff.load()

### processing

@babel.localeselector
def get_locale():
    if 'lang' in request.args:
        session['lang'] = request.args.get('lang')
    lang = request.accept_languages.best_match(['de', 'en'])
    if 'lang' not in session:
        if lang is not None:
            return lang
        return None
    return session.get('lang')

@app.context_processor
def context_processor():
    """add "lang" variable to context (for babel)
    """
    if 'lang' in session:
        return {'lang':session.get('lang')}
    return {}

@app.before_request
def before_request():
    staff.check_if_changed()
    bib.check_if_changed()

### errors

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html')

### routes

@app.route('/')
def main():
    return render_template('main.html', navi_home=True)

@app.route('/about/')
def about():
    return render_template('about.html', navi_about=True)

@app.route('/authors/')
def authors():
    return render_template('staff.html', 
                           current=staff.get_staff_list(),
                           former=staff.get_staff_list(current=False),
                           navi_authors=True
                           )

@app.route('/authors/<lastname>/<firstname>/')
def author_byname(lastname, firstname):
    """ show all bib entries of one author as <pre>
    with download links for all bib entries
    """
    return render_template('list.html', 
                           title=gettext("Bibliography of %(ln)s, %(fn)s", 
                                         ln=lastname, fn=firstname),
                           lastname=lastname,
                           firstname=firstname,
                           entries=bib.search_by_author(lastname, firstname),
                           navi_authors=True)

@app.route('/authors/<lastname>/<firstname>/<typ>/')
def author_byname_typ(lastname, firstname, typ='bib'):
    """returns all bib/htmls of one author
    """
    result = ""
    elements = bib.search_by_author(lastname, firstname)
    if typ == 'bib':
        return render_template('bib.html', 
                               title="BibTeX",
                               entries=elements,
                               navi_authors=True)
    elif typ == 'html':
        return render_template('html.html', entries=elements)

@app.route('/list/')
@app.route('/list/year/')
@app.route('/list/year/<year>/')
def list_year(year=None):
    if year:
        entries = bib.search_by_year(year)
        title = gettext("All Publications in %(value)s", value=year)
    else:
        entries = bib.pubs
        title = gettext("All Publications")
    return render_template('list.html', 
                           entries=entries,
                           year=year,
                           title=title,
                           navi_all=True)

@app.route('/entry/<entry>/')
@app.route('/entry/<entry>/<format>/')
def entry(entry, format='bib'):
    """return entry as bib or html
    """
    result = bib.get_target_for_element(entry)
    if result:
        if format=='bib':
            return render_template('bib.html', 
                                   title="BibTeX",
                                   entries=[result],
                                   navi_authors=True)
        else:
            return Response(response=result.get('bibtex').encode('utf-8'),
                            content_type="text/plain; charset=utf-8")
    else:
        abort(404)
       

@app.route('/search/', methods=['GET', 'POST'])
def search():
    """search -- returns result only if minimum one of the fields was changed
    """
    used = False
    if request.method == 'POST':
        result = bib.pubs
        if request.form['q_title']:
            used = True
            result1 = bib.search_by_title(request.form['q_title'], bib.pubs)
            result = bib.search_by_keyword(request.form['q_title'], bib.pubs)
            result = result + result1
        if request.form['q_author']:
            used = True
            lastname, firstname = request.form['q_author'].split(',')
            result = bib.search_by_author(lastname, firstname, result)
        if request.form['q_year']:
            used = True
            result = bib.search_by_year(request.form.getlist('q_year'), result)
        if used and request.form['format']:
            if request.form['format'] == 'html':
                return render_template('list.html', 
                                       entries=result, 
                                       title=gettext("Search results"))
            if request.form['format'] == 'bibtex':
                return render_template('bib.html', 
                                       title=gettext("Search results"),
                                       entries=result,
                                       navi_search=True)

    return render_template('search.html',
                           years= bib.get_years_list(),
                           current=staff.get_staff_list(),
                           former=staff.get_staff_list(current=False),
                           navi_search=True)

@app.template_filter('striptex')
def striptex(s):
    return bibmod.striptex(s)


### main

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
