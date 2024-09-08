from os.path import join, exists
from pathlib import Path
import tempfile

from building3d.paths.wildcardpath import WildcardPath


def fill_dir(parent: str, num_sub: int, num_subsub: int) -> None:
    p = Path(parent)
    num_sub = 5
    num_subsub = 3
    for i in range(num_sub):
        sub = p / f"a_{i}"
        sub.mkdir()
        for k in range(num_subsub):
            subsub = sub / f"b_{i}_{k}"
            subsub.mkdir()


def test_wildcardpath_get_matching_paths():
    with tempfile.TemporaryDirectory() as parent:
        num_sub = 5
        num_subsub = 3
        fill_dir(parent, num_sub, num_subsub)

        wp = WildcardPath("a_<n1>")
        parent = str(parent)
        assert len(wp.get_matching_paths(parent)) == num_sub
        d = wp.get_matching_paths_dict_values(parent)
        assert len(list(d.items())) == num_sub
        for i in range(num_sub):
            assert d[join(parent, f"a_{i}")] == {"n1": i}

        wp = WildcardPath("a_<n1>/b_<n1>_<n2>")
        parent = str(parent)
        assert len(wp.get_matching_paths(parent)) == num_sub * num_subsub
        assert len(wp.get_matching_paths(parent, n1=1, n2=1)) == 1
        assert len(wp.get_matching_paths(parent, n1=1)) == num_subsub


def test_wildcardpath_get_matching_paths_dict_values():
    with tempfile.TemporaryDirectory() as parent:
        num_sub = 5
        num_subsub = 3
        fill_dir(parent, num_sub, num_subsub)

        wp = WildcardPath("a_<n1>/b_<n1>_<n2>")
        d = wp.get_matching_paths_dict_values(parent)
        assert len(list(d.items())) == num_sub * num_subsub
        for i in range(num_sub):
            for k in range(num_subsub):
                assert d[join(parent, f"a_{i}/b_{i}_{k}")] == {"n1": i, "n2": k}


def test_wildcardpath_get_matching_paths_namedtuple_keys():
    with tempfile.TemporaryDirectory() as parent:
        num_sub = 5
        num_subsub = 3
        fill_dir(parent, num_sub, num_subsub)

        wp = WildcardPath("a_<n1>/b_<n1>_<n2>")
        d = wp.get_matching_paths_namedtuple_keys(parent)
        assert d[wp.Case(n1=1, n2=1)] == join(parent, "a_1/b_1_1")
        assert d[wp.Case(n1=1, n2=2)] == join(parent, "a_1/b_1_2")


def test_wildcardpath_mkdir():
    with tempfile.TemporaryDirectory() as parent:
        wp = WildcardPath("a_<n1>/b_<n2>/c_<n1>_<n2>_<n3>")
        wp.mkdir(parent, n1=1, n2=2, n3=3)

        assert exists(join(parent, "a_1", "b_2", "c_1_2_3"))
