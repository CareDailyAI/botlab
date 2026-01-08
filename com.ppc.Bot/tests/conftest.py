# content of conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--variables", action="store", nargs="+", help="*.variable files to preload into test cases"
    )
    parser.addoption(
        "--location_id", action="store", help="Location ID to preload into test cases"
    )

    


@pytest.fixture(scope="class")
def bot_variables(request):
    request.cls.bot_variables = request.config.getoption("--variables")

@pytest.fixture(scope="class")
def location_id(request):
    location_id = request.config.getoption("--location_id")
    request.cls.location_id = int(location_id) if location_id is not None else None
        