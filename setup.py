#!/usr/bin/env python

from distutils.core import setup

setup(name='timetravel',
      version='0.1',
      description='File watcher for git repositories',
      author='Xy Ziemba',
      author_email='xy.ziemba@gmail.com',
      url='https://bitbucket.org/xyziemba/timetravel',
      scripts=['src/timetravel-cli.py'],
      packages=['timetravel'],
      package_dir={'': 'src'})
