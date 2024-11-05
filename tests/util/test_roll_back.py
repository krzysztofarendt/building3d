from building3d.util.roll_back import roll_back


def test_roll_back():
    a = [1, 2, 3]
    a = roll_back(a)
    assert a == [2, 3, 1]
    a = roll_back(a)
    assert a == [3, 1, 2]
    a = roll_back(a)
    assert a == [1, 2, 3]
