"""Custom exceptions"""


class GeometryError(Exception):
    """Error due to incorrectly defined geometry."""

    def __init__(self, message):
        super().__init__("GeometryError: " + message)


class TriangulationError(Exception):
    """Error raised when polygon triangulation fails."""

    def __init__(self, message):
        super().__init__("TriangulationError: " + message)
