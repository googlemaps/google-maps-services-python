import sys


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


if sys.version_info <= (2, 4):
  error = 'Requires Python Version 2.5 or above... exiting.'
  print >> sys.stderr, error
  sys.exit(1)


requirements = [
    'requests',
]

setup(name='googlemaps',
      version='2.0-dev',
      description='API Client library for Google Maps',
      scripts=[],
      url='https://github.com/googlemaps/google-maps-services-python',
      packages=['googlemaps'],
      license='Apache 2.0',
      platforms='Posix; MacOS X; Windows',
      setup_requires=requirements,
      install_requires=requirements,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.2',
                   'Topic :: Internet',
                   ]
      )
