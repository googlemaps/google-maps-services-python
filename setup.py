from setuptools import setup


requirements = ["requests>=2.20.0,<3.0"]

with open("README.md") as f:
    readme = f.read()

with open("CHANGELOG.md") as f:
    changelog = f.read()


setup(
    name="googlemaps",
    version="4.6.0",
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
