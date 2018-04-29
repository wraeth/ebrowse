#!/usr/bin/env python3

from setuptools import setup, find_packages

import ebrowse

setup(name=ebrowse.__NAME__,
      version=ebrowse.__VERSION__,
      description=ebrowse.__DESCRIPTION__,
      author=ebrowse.__AUTHOR__,
      author_email=ebrowse.__AUTHOR_EMAIL__,
      url=ebrowse.__UPSTREAM__,
      license=ebrowse.__LICENSE__,

      entry_points={
          'console_scripts': [
              'ebrowse = ebrowse.cli:main'
          ]
      },

      platforms=['Linux'],
      packages=find_packages()
)
