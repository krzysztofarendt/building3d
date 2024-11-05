import pytest
import numpy as np
from pathlib import Path
import tempfile

from building3d.display.plot_objects import plot_objects


class MockMeshObject:
    def get_mesh(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        faces = np.array([[0, 1, 2]])
        return verts, faces


class MockLineObject:
    def get_lines(self):
        verts = np.array([[0, 0, 0], [1, 0, 0]])
        lines = np.array([[0, 1]])
        return verts, lines


class MockPointObject:
    def get_points(self):
        return np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])


def test_plot_objects_empty():
    with pytest.raises(ValueError, match="Nothing to plot"):
        plot_objects(())


def test_plot_objects_invalid_colors():
    obj = MockMeshObject()
    with pytest.raises(ValueError, match="Number of colors must be same"):
        plot_objects((obj,), colors=[(1, 0, 0), (0, 1, 0)])


def test_plot_objects_mesh():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_plot.png"
        obj = MockMeshObject()
        plot_objects((obj,), output_file)  # Should not raise any exception
        assert output_file.exists()


def test_plot_objects_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_plot.png"
        obj = MockLineObject()
        plot_objects((obj,), output_file)  # Should not raise any exception
        assert output_file.exists()


def test_plot_objects_points():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_plot.png"
        obj = MockPointObject()
        plot_objects((obj,), output_file)  # Should not raise any exception
        assert output_file.exists()


def test_plot_objects_with_colors():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_plot.png"
        obj1 = MockMeshObject()
        obj2 = MockLineObject()
        colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        plot_objects((obj1, obj2), output_file, colors=colors)  # Should not raise any exception
        assert output_file.exists()


def test_plot_objects_save_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_plot.png"
        obj = MockMeshObject()
        plot_objects((obj,), output_file=str(output_file))
        assert output_file.exists()


def test_plot_objects_multiple_types():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_plot.png"
        obj1 = MockMeshObject()
        obj2 = MockLineObject()
        obj3 = MockPointObject()
        plot_objects((obj1, obj2, obj3), output_file)  # Should not raise any exception
        assert output_file.exists()

def test_plot_objects_invalid_object():
    class InvalidObject:
        pass

    obj = InvalidObject()
    with pytest.raises(AssertionError):
        plot_objects((obj,))

