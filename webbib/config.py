#
#
#

class Config(object):
    """ BaseConfig
    """
    # generate a new one: import os; os.urandom(24)
    SECRET_KEY = 'fhttzWoxxv0mgxxwzoJpaqvfqocbpqkkfzc]izeog6ovivvdtr'

class ExampleConfig(Config):
    # relative to webbib path
    BIB_FILENAME = 'examples/example.bib'
    STAFF_FILENAME = 'examples/staff.xml'
