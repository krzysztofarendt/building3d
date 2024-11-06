import pytest
import uuid

from building3d.random import random_id, random_within, random_between


def test_random_id_default():
    """Test random_id() returns valid UUID string."""
    id = random_id()
    assert len(id) == 36
    assert isinstance(id, str)
    # Verify it's a valid UUID
    uuid.UUID(id)


@pytest.mark.parametrize("size", [1, 8, 16, 32])
def test_random_id_with_size(size):
    """Test random_id() with different valid sizes."""
    id = random_id(size)
    assert len(id) == size
    assert isinstance(id, str)
    assert "-" not in id


def test_random_id_invalid_size():
    """Test random_id() raises error for invalid sizes."""
    with pytest.raises(ValueError, match="must be greater than 0"):
        random_id(0)
    with pytest.raises(ValueError, match="must be greater than 0"):
        random_id(-1)
    with pytest.raises(ValueError, match="maximum length.*is 36"):
        random_id(33)


def test_random_within():
    """Test random_within() generates values in correct range."""
    # Test with default lim=1.0
    for _ in range(100):
        val = random_within()
        assert -1.0 <= val < 1.0

    # Test with custom lim
    lim = 5.0
    for _ in range(100):
        val = random_within(lim)
        assert -lim <= val < lim

    # Test with lim=0
    assert random_within(0) == 0.0


def test_random_between():
    """Test random_between() generates values in correct range."""
    lo, hi = 2.0, 5.0
    for _ in range(100):
        val = random_between(lo, hi)
        assert lo <= val < hi

    # Test with swapped lo/hi values
    val = random_between(hi, lo)
    assert lo <= val < hi

    # Test with equal values
    val = random_between(2.0, 2.0)
    assert val == 2.0
