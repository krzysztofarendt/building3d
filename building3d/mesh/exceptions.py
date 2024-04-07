"""Custom exceptions"""

class MeshError(Exception):
    """Error due to incorrectly defined Mesh."""

    def __init__(self, message):
        super().__init__("MeshError: " + message)

