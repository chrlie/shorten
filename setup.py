#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shorten import __version__

try:
   from setuptools import setup
   kw = {}

except ImportError:
   from distutils.core import setup
   kw = {}

with open('readme.rst', 'rb+') as readme:
   long_description = readme.read()

setup(
   name = 'shorten',
   packages = ['shorten'],
   version = __version__,
   description = 'A Python library for generating short URLs.',

   author = 'Charlie Liban',
   author_email = 'charlie@tyrannosaur.ca',
   maintainer='Charlie Liban',
   maintainer_email='charlie@tyrannosaur.ca',   

   url = 'https://github.com/tyrannosaur/shorten',
   download_url = 'https://github.com/tyrannosaur/shorten/zipball/master',
   keywords = ['redis','internet','url'],
   classifiers = [
      'Programming Language :: Python',
      'License :: OSI Approved :: MIT License',
      'Topic :: Internet :: WWW/HTTP',
   ],

   license = 'MIT License',
   long_description = long_description,
   **kw
)     
