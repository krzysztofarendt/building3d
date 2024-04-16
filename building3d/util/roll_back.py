def roll_back(x: list) -> list:
    """Shifts the list x by -1. First elements is moved to the end."""
    xnew = [x[i] for i in range(1, len(x))]
    xnew.append(x[0])
    return xnew
