from numba import njit


@njit
def jit_print(verbose:bool, *args) -> None:
    """Print wrapper with a verbosity flag.

    This function is used to turn on/off printing in all JIT-compiled functions.

    Args:
        verbose (bool): If True, prints *args
        args: Arguments to print

    Returns:
        None
    """
    if verbose:
        print(*args)
