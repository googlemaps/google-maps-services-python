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
    'requests>=2.11.1,<3.0',
]

setup(name='googlemaps',
      version='2.5.1-dev',
      description='Python client library for Google Maps API Web Services',
      scripts=[],
      url='https://github.com/googlemaps/google-maps-services-python',
      packages=['googlemaps'],
      license='Apache 2.0',
      platforms='Posix; MacOS X; Windows',
      setup_requires=requirements,
      install_requires=requirements,
      test_suite='googlemaps.test',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Internet',
                   ]
      )
