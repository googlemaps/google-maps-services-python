import sys
import io
from setuptools import setup


requirements = ["requests>=2.20.0,<3.0"]

# use io.open until python2.7 support is dropped
with io.open("README.md", encoding="utf8") as f:
    readme = f.read()

with io.open("CHANGELOG.md", encoding="utf8") as f:
    changelog = f.read()


setup(
    name="googlemaps",
    version="4.2.0",
    description="Python client library for Google Maps Platform",
    long_description=readme + changelog,
    long_description_content_type="text/markdown",
    scripts=[],
    url="https://github.com/googlemaps/google-maps-services-python",
    packages=["googlemaps"],
    license="Apache 2.0",
    platforms="Posix; MacOS X; Windows",
    setup_requires=requirements,
    install_requires=requirements,
    test_suite="googlemaps.test",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
    ],
    python_requires='>=3.5'
)
