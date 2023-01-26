# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup


requirements = ["requests>=2.20.0,<3.0"]

with open("README.md") as f:
    readme = f.read()

with open("CHANGELOG.md") as f:
    changelog = f.read()


setup(
    name="googlemaps",
    version="4.10.0",
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
