import pytest

import building3d


def test_random_id():
    assert len(building3d.random_id()) == 36
    for i in range(1, 33):
        assert len(building3d.random_id(i)) == i
    with pytest.raises(ValueError):
        assert len(building3d.random_id(0)) == 0
    with pytest.raises(ValueError):
        building3d.random_id(-1)
    with pytest.raises(ValueError):
        building3d.random_id(37)


def test_random_within():
    for i in range(100):
        r = building3d.random_within(i)
        if i == 0:
            assert r == 0
        else:
            assert r > -i and r < i
