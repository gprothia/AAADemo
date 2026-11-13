import os

import httpx
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "ac(id): acceptance criterion this test verifies")


@pytest.fixture(scope="session")
def api():
    base = os.environ.get("API_BASE_URL", "http://localhost:8080")
    with httpx.Client(base_url=base, timeout=15) as client:
        yield client


def pytest_collection_modifyitems(items):
    # Put the AC ID into the JUnit report so failures map straight back to the spec.
    for item in items:
        for mark in item.iter_markers("ac"):
            item.user_properties.append(("acceptance_criterion", mark.args[0]))
