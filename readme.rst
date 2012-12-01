
========
 WebBib
========


Introduction
============

The WebBib was written as replacement for an old Tomcat based webservice.
The original version read an xml file gerated by bib2xml.
After some problems with the convertion we started to use pybtex for reading
the original bibtex files.
The staff.xml files stayed the same.

For development see https://github.com/mfa/webbib/

In production: http://www.ims.uni-stuttgart.de/bibliographie/


Install
=======

* system requirements (RHEL)

::

  yum install libxml2-devel libxslt-devel libyaml-devel

* install:

::

  virtualenv --distribute env_webbib
  . env_webbib/bin/activate
  pip install -r requirements.txt

* run (testing):

::

  . env_webbib/bin/activate
  # install webbib
  python setup.py install
  # run example
  cd example
  webbib-cli

* translations:

::

  pybabel extract -F babel.cfg -o messages.pot .
  pybabel update -i messages.pot -d translations
  pybabel compile -d translations

  # INIT (new languages)
  pybabel init -i messages.pot -d translations -l de
