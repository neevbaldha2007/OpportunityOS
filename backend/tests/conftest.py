"""Run application tests with disposable data and no real SerpApi requests."""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

_test_directory = TemporaryDirectory(prefix="opportunityos-tests-")
_test_database = Path(_test_directory.name) / "opportunityos.db"
os.environ.update({
    "APP_ENV": "development",
    "API_PREFIX": "",
    "DATABASE_URL": f"sqlite:///{_test_database.as_posix()}",
    "JWT_SECRET": "isolated-tests-only-secret-not-for-production-123456",
    "CORS_ORIGINS": "http://localhost:5173",
    "DEMO_MODE": "true",
    "SERPAPI_API_KEY": "",
})


@pytest.fixture(scope="session")
def anyio_backend():
    # The application uses asyncio tasks and locks.
    return "asyncio"


def pytest_sessionfinish(session, exitstatus):
    database_module = sys.modules.get("app.db")
    if database_module is not None:
        database_module.engine.dispose()
    _test_directory.cleanup()
