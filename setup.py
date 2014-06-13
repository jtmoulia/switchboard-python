#!/usr/bin/env python

from setuptools import setup

setup(name='switchboard',
      version='0.1.0',
      author='jtmoulia',
      author_email='jtmoulia@pocketknife.io',
      description='Python switchboard utilites',
      long_description=open('readme.rst').read(),
      license='license.txt',
      packages=['switchboard'],
      install_requires=['ws4py == 0.3.4'],
      test_suite = 'test.test_switchboard')
