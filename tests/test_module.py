"""Here are the actual test for the module: run with ``pytest test_module.py``.
There is no need to import conftest it happens automatically.
"""
import pytest
# import pprint as pp


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.mark.parametrize(
    # These are the variabe names by which the parameters in the list will be
    # available in the test function
    "var1,var2,var3",
    # Each element in this list represents a single parameter
    [
        # Some dummy parameters, place what you want here
        (("row0_var1", "row0_var2", "row0_var3")),
        (("row1_var1", "row1_var2", "row1_var3")),
        (("row2_var1", "row2_var2", "row2_var3")),
    ]
)
def test_param(return_fixture, var1, var2, var3):
    """Here we are using a fixture from our conftest.py (return_fixture) and the
    test parameters. Run pytest with the -s flag to see print statements.
    """
    print(return_fixture)
    print(var1)
    print(var2)
    print(var3)
    assert var1.endswith("var1"), "bad var1 variable"
    assert var2.endswith("var2"), "bad var2 variable"
    assert var3.endswith("var3"), "bad var3 variable"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.mark.xfail()
@pytest.mark.dependency()
def test_external_resource_available(resource_available):
    """A dummy test that is designed to test if an external resource is
    available and fail if not. This is a pytest-dependency (an external module
    that can be installed with pip). So, other tests that depend on this
    resource should mark this test as a dependency, then they all will be
    skipped if the resource is not available. This one will fail though. If it
    is not there then the remainder of the tests are skipped. The xfail mark
    means that we are expecting that this might fail. If it does then you will
    see a small x (xfail), if it does not then you will see a large X (xpass).
    """
    assert resource_available, "resource not available"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.mark.dependency(depends=['test_external_resource_available'])
def test_should_run(resource_available):
    """This test mimicks a test that should only run if an external resource is
    available (which in this case it is).
    """
    # Use the resource_available fixture for the test, change to whatever
    # you need
    assert resource_available


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.mark.xfail()
@pytest.mark.dependency()
def test_external_resource_not_available(resource_not_available):
    """A dummy test that is designed to test if an external resource is
    available and fail if not. This is a pytest-dependency (an external module
    that can be installed with pip). So, other tests that depend on this
    resource should mark this test as a dependency, then they all will be
    skipped if the resource is not available. This one will fail though. If it
    is not there then the remainder of the tests are skipped. The xfail mark
    means that we are expecting that this might fail. If it does then you will
    see a small x (xfail), if it does not then you will see a large X (xpass).
    """
    assert resource_not_available, "resource not available"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@pytest.mark.dependency(depends=['test_external_resource_not_available'])
def test_should_not_run(resource_available):
    """This test mimicks a test that should only run if an external resource is
    available (which in this case it is).
    """
    # Use the resource_available fixture for the test, change to whatever
    # you need
    assert resource_available


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def test_exception():
    """This test demonstrates how to test that a specific exception has been
    raised.
    """
    with pytest.raises(TypeError) as the_error:
        raise TypeError("I was expecting this error")

    # Now make sure that the correct error massage was raised
    assert the_error.value.args[0] == "I was expecting this error", \
        "wrong error massage"
