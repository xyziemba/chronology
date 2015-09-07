#!/usr/bin/env python

from distutils.core import setup

setup(name='chronology',
      version='0.0.1',
      description='File watcher for git repositories',
      author='Xy Ziemba',
      author_email='xy.ziemba@gmail.com',
      url='https://github.com/xyziemba/chronology',
      scripts=['src/chronology-cli.py'],
      packages=['chronology'],
      package_dir={'': 'src'})
