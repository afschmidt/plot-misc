"""Fixtures (re-usable data components and settings) for tests
"""
import pytest


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.fixture()
def return_fixture(tmpdir):
    """Illustrating returning a tmpdir (another builtin pytest fixture) from
    pytest (this is magically destroyed) after the test.
    """
    return tmpdir


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.fixture()
def yield_fixture(tmpdir):
    """Values can also be yielded from a fixture. Allowing you to do stuff
    after
    """
    yield tmpdir

    # Do something else here after the test has run


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.fixture(scope="session", autouse=True)
def session_scope():
    """Unlike the two fixtures above that are loaded each time they are called
    from a test. The session scope fixtures are loaded once when the test
    module is run.
    """
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.fixture()
def resource_available(tmpdir):
    """This mimics a fixture that will supply a path to an external resource.
    If the resource is available the fixture will return it, if not then it
    will return False. The calling test can then ``assert resource_available``
    and fail appropriately.
    """
    return tmpdir


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.fixture()
def resource_not_available():
    """This mimics a fixture that will supply a path to an external resource.
    If the resource is available the fixture will return it, if not then it
    will return False. The calling test can then ``assert resource_available``
    and fail appropriately.
    """
    return False
