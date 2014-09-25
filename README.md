Generating documentation:

    $ sphinx-build -b html docs docs/html

Installing dependencies:

    $ pip install requests responses

Running tests:

    $ git submodule update --init
    $ python -m unittest discover
