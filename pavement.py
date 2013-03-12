from paver.easy import *
from pkg_resources import load_entry_point

@task
def test():
    """ run py.test
    """
    load_entry_point('pytest', 'console_scripts', 'py.test')([])

@task
def cov():
    """ run py.test with coverage plugin
    """
    load_entry_point('pytest', 'console_scripts', 'py.test')(["--cov=src"])
