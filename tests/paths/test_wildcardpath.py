from os.path import join, exists
from pathlib import Path
import tempfile

from building3d.paths.wildcardpath import WildcardPath


def test_wildcardpath_get_matching():
    with tempfile.TemporaryDirectory() as parent:
        p = Path(parent)

        num_sub = 5
        num_subsub = 3
        for i in range(num_sub):
            sub = p / f"a_{i}"
            sub.mkdir()

            for k in range(num_subsub):
                subsub = sub / f"b_{i}_{k}"
                subsub.mkdir()

        wp = WildcardPath("a_<n1>")
        parent = str(parent)
        assert len(wp.get_matching_paths(parent)) == num_sub
        d = wp.get_matching_paths_and_values(parent)
        assert len(list(d.items())) == num_sub
        for i in range(num_sub):
            assert d[join(parent, f"a_{i}")] == {"n1": i}

        wp = WildcardPath("a_<n1>/b_<n1>_<n2>")
        parent = str(parent)
        assert len(wp.get_matching_paths(parent)) == num_sub * num_subsub

        d = wp.get_matching_paths_and_values(parent)
        assert len(list(d.items())) == num_sub * num_subsub
        for i in range(num_sub):
            for k in range(num_subsub):
                assert d[join(parent, f"a_{i}/b_{i}_{k}")] == {"n1": i, "n2": k}


def test_wildcardpath_mkdir():
    with tempfile.TemporaryDirectory() as parent:
        p = Path(parent)

        wp = WildcardPath("a_<n1>/b_<n2>/c_<n1>_<n2>_<n3>")
        wp.mkdir(parent, n1=1, n2=2, n3=3)

        assert exists(join(parent, "a_1", "b_2", "c_1_2_3"))
