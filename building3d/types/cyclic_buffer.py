import numpy as np
from numba import njit


@njit
def cyclic_buf(
    buffer: np.ndarray, head: int, tail: int, element: np.ndarray, buffer_size: int
):
    """
    Inserts an element into a cyclic (circular) buffer and updates the head and tail pointers.

    This function efficiently manages a fixed-size cyclic buffer using manual index handling
    and Numba's JIT compilation for speed. When the buffer is full, the oldest element is
    overwritten.

    Args:
        buffer (np.ndarray): A pre-allocated 1D NumPy array that serves as the cyclic buffer.
            It should have a fixed size.
        head (int): The index where the next element will be written. Wraps around when it
            reaches the end of the buffer.
        tail (int): The index where the next element will be read from. When the buffer is full,
            this index is incremented to overwrite the oldest element.
        element (np.ndarray): The new element to insert into the buffer at the position indicated
            by `head`.
        buffer_size (int): The fixed size of the buffer, which should match the length of the
            `buffer` array.

    Returns:
        tuple:
            np.ndarray: The updated cyclic buffer with the new element inserted.
            int: The updated index pointing to the next write position in the buffer (`head`).
            int: The updated index pointing to the next read position (`tail`), moved only if the
            buffer is full and an element has been overwritten.

    Notes:
        - The buffer uses manual wrap-around (circular indexing) with modulo arithmetic.
        - If the `head` pointer reaches the `tail` pointer, the buffer is considered full, and the
          oldest element (at `tail`) will be overwritten.
        - The function is compiled using Numba's `nopython` mode for high performance, which means
          all types must be explicitly defined at compile time.

    Example:
        >>> buffer_size = 5
        >>> buffer = np.zeros(buffer_size, dtype=np.float32)
        >>> head, tail = 0, 0
        >>> new_val = np.random.random(3)
        >>> buffer, head, tail = cyclic_buffer(buffer, head, tail, new_val, buffer_size)
        >>> print(buffer, head, tail)
        [[0.39438182 0.95590234 0.39243249]
         [0.         0.         0.        ]
         [0.         0.         0.        ]
         [0.         0.         0.        ]
         [0.         0.         0.        ]]
        Head: 1 Tail: 0
    """
    # Insert the new element at the head position
    buffer[head, :] = element
    head = (head + 1) % buffer_size  # Circular increment

    # If head catches up with tail, we move the tail to maintain buffer size
    if head == tail:
        tail = (tail + 1) % buffer_size  # Overwrite oldest element

    return buffer, head, tail


@njit
def convert_to_contiguous(buffer, head, tail):
    """
    Converts the current state of the cyclic buffer to a contiguous array
    where the tail becomes index 0 and the head becomes the last element (-1).

    Args:
        buffer (np.ndarray): Cyclic buffer (2D or 1D) to be flattened into a contiguous array.
        head (int): Index where the next element will be written (end of buffer).
        tail (int): Index where the oldest element is located (start of the logical buffer).

    Returns:
        np.ndarray: A contiguous array with elements arranged in logical order from tail to head.
    """
    if head == tail:
        # Buffer is empty
        return np.empty((0,) + buffer.shape[1:], dtype=buffer.dtype)

    if head > tail:
        # Tail to head is a single slice
        return buffer[tail:head]

    # Tail to head wraps around
    return np.vstack((buffer[tail:], buffer[:head]))


if __name__ == "__main__":
    # Example
    buffer_size = 5
    buffer = np.zeros((buffer_size, 3), dtype=np.float32)
    head, tail = 0, 0

    for i in range(10):
        new_val = np.random.random(3)
        buffer, head, tail = cyclic_buf(buffer, head, tail, new_val, buffer_size)
        print(i)
        print(buffer)
