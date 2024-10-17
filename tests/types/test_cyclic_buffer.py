import numpy as np

from building3d.types.cyclic_buffer import cyclic_buf


def test_cyclic_buf_basic():
    buffer_size = 5
    buffer = np.zeros((buffer_size, 3), dtype=np.float32)
    head, tail = 0, 0
    element = np.array([1.0, 2.0, 3.0], dtype=np.float32)

    buffer, head, tail = cyclic_buf(buffer, head, tail, element, buffer_size)

    assert head == 1
    assert tail == 0
    np.testing.assert_array_equal(buffer[0], element)
    np.testing.assert_array_equal(buffer[1:], np.zeros((4, 3), dtype=np.float32))


def test_cyclic_buf_full():
    buffer_size = 3
    buffer = np.zeros((buffer_size, 2), dtype=np.float32)
    head, tail = 0, 0

    for i in range(4):
        element = np.array([float(i), float(i + 1)], dtype=np.float32)
        buffer, head, tail = cyclic_buf(buffer, head, tail, element, buffer_size)

    assert head == 1  # New element would be written at this index
    assert tail == 2  # Oldest element is at this index
    np.testing.assert_array_equal(
        buffer, np.array([[3.0, 4.0], [1.0, 2.0], [2.0, 3.0]], dtype=np.float32)
    )


def test_cyclic_buf_wrap_around():
    buffer_size = 4
    buffer = np.zeros((buffer_size, 1), dtype=np.float32)
    head, tail = 0, 0

    for i in range(6):
        element = np.array([float(i)], dtype=np.float32)
        buffer, head, tail = cyclic_buf(buffer, head, tail, element, buffer_size)

    assert head == 2  # New element would be written at this index
    assert tail == 3  # Oldest element is at this index
    np.testing.assert_array_equal(
        buffer, np.array([[4.0], [5.0], [2.0], [3.0]], dtype=np.float32)
    )


def test_cyclic_buf_single_element():
    buffer_size = 1
    buffer = np.zeros((buffer_size, 3), dtype=np.float32)
    head, tail = 0, 0

    element1 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    buffer, head, tail = cyclic_buf(buffer, head, tail, element1, buffer_size)

    assert head == 0
    assert tail == 0
    np.testing.assert_array_equal(buffer[0], element1)

    element2 = np.array([4.0, 5.0, 6.0], dtype=np.float32)
    buffer, head, tail = cyclic_buf(buffer, head, tail, element2, buffer_size)

    assert head == 0
    assert tail == 0
    np.testing.assert_array_equal(buffer[0], element2)
