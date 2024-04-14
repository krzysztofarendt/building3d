from building3d import random_within


def test_random_within():
    for _ in range(1000):
        lim = 0.1
        v = random_within(lim)
        assert v > -lim and v < lim

    assert random_within(0) == 0
    assert random_within(0.0) == 0
