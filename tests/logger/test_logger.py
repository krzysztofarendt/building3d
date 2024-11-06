"""
Tests written by Claude3.5 Sonnet.

The test file includes:

1. A cleanup fixture to remove test log files after each test
2. Test for default logger initialization checking:
   - Log file creation
   - Logger level
   - Handler configuration
3. Test for custom path initialization checking:
   - Directory creation
   - Log file creation
   - Handler configuration

Note that we're using pytest's fixture system to clean up the log files after
each test to avoid leaving test artifacts behind.

When a fixture uses `yield`, pytest splits the fixture execution into two
parts:

1. **Setup Phase**: Everything before the `yield` statement runs at the
   beginning
2. **Teardown Phase**: Everything after the `yield` statement runs at
   the end

Here's the execution flow:
```
Test 1 starts
↓
cleanup_logfiles runs (yield point)
↓
test_init_logger_default() executes
↓
cleanup_logfiles cleanup runs (after yield)
↓
Test 2 starts
↓
cleanup_logfiles runs (yield point)
↓
test_init_logger_custom_path() executes
↓
cleanup_logfiles cleanup runs (after yield)
```

This pattern ensures that each test starts with a clean state (no existing log files)
and doesn't leave any artifacts behind after completion.
"""
import logging
from pathlib import Path

import pytest

from building3d.config import LOG_FILE, LOG_LEVEL
from building3d.logger import init_logger


@pytest.fixture
def cleanup_logfiles():
    """Remove test log files after each test."""
    yield
    if Path(LOG_FILE).exists():
        Path(LOG_FILE).unlink()

    test_log = Path("test_logs/test.log")
    if test_log.exists():
        test_log.unlink()
    if test_log.parent.exists():
        test_log.parent.rmdir()


def test_init_logger_default(cleanup_logfiles):
    """Test logger initialization with default settings."""
    init_logger()

    assert Path(LOG_FILE).exists()
    root_logger = logging.getLogger()
    assert root_logger.level == LOG_LEVEL

    handlers = root_logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.FileHandler)
    assert handlers[0].baseFilename == str(Path(LOG_FILE).absolute())


def test_init_logger_custom_path(cleanup_logfiles):
    """Test logger initialization with custom logfile path."""
    custom_logfile = "test_logs/test.log"
    init_logger(custom_logfile)

    assert Path(custom_logfile).exists()
    assert Path(custom_logfile).parent.exists()

    root_logger = logging.getLogger()
    handlers = root_logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.FileHandler)
    assert handlers[0].baseFilename == str(Path(custom_logfile).absolute())
