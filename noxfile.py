import nox

SUPPORTED_PY_VERSIONS = ["3.7", "3.8", "3.9", "3.10"]


def _install_dev_packages(session):
    session.install("-e", ".")


def _install_test_dependencies(session):
    session.install("pytest")
    session.install("pytest-cov")
    session.install("responses")


def _install_doc_dependencies(session):
    session.install("sphinx")


@nox.session(python=SUPPORTED_PY_VERSIONS)
def tests(session):
    _install_dev_packages(session)
    _install_test_dependencies(session)

    session.install("pytest")
    session.run("pytest")

    session.notify("cover")


@nox.session
def cover(session):
    """Coverage analysis."""
    session.install("coverage")
    session.install("codecov")
    session.run("coverage", "report", "--show-missing")
    session.run("codecov")
    session.run("coverage", "erase")


@nox.session(python="3.6")
def docs(session):
    _install_dev_packages(session)
    _install_doc_dependencies(session)

    session.run("rm", "-rf", "docs/_build", external=True)

    sphinx_args = [
        "-a",
        "-E",
        "-b",
        "html",
        "-d",
        "docs/_build/doctrees",
        "docs",
        "docs/_build/html",
    ]

    sphinx_cmd = "sphinx-build"

    session.run(sphinx_cmd, *sphinx_args)


@nox.session()
def distribution(session):
    session.run("bash", ".github/scripts/distribution.sh", external=True)
    session.run("python", "-c", "import googlemaps")
