#!/usr/bin/env python

from setuptools import setup

setup(name='switchboard-python',
      version='0.1.0',
      author='jtmoulia',
      author_email='jtmoulia@pocketknife.io',
      description='Python switchboard utilites',
      long_description=open('readme.rst').read(),
      keywords=['email', 'worker', 'websocket'],
      url='https://github.com/jtmoulia/switchboard-python',
      download_url='https://github.com/jtmoulia/switchboard-python/tarball/0.1.0',
      license=open('license.txt').read(),
      packages=['switchboard', 'aplus'],
      install_requires=['ws4py == 0.3.4'],
      test_suite='test.test_switchboard')
