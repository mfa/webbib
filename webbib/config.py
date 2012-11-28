#
#
#

class Config(object):
    """ BaseConfig
    """
    # generated using: import os; os.urandom(24)
    SECRET_KEY = 'fhttzWoxxv0mgxxwzoJpaqvfqocbpqkkfzc]izeog6ovivvdtr'

class ExampleConfig(Config):
    # relative to webbib path
    BIB_FILENAME = 'examples/example.bib'
    STAFF_FILENAME = 'examples/staff.xml'
