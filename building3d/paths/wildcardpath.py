from collections import defaultdict
from pathlib import Path
import re


class WildcardPath:
    """Custom path class which allows to use wildcards which can be read or replaced with numbers.

    For example, for the following directory structure:
    - parent_dir
        - sub_dir_0
        - sub_dir_1
            - file_1_0.csv
            - file_1_1.csv

    The output for this method would be:
    ```python
    >>> wp = WildcardPath("sub_dir_<job>/file_<job>_<step>.csv")
    >>> wp.get_matching_paths_and_values("parent_dir")
    {
        "parent_dir/sub_dir_1/file_1_0.csv": {"job": 1, "step": 0},
        "parent_dir/sub_dir_1/file_1_1.csv": {"job": 1, "step": 1},
    }
    ```

    Directories can be also created by replacing wildcards with chosem integers, e.g.:
    ```python
    >>> wp = WildcardPath("sub_dir_<job>/case_dir_<case>")
    >>> wp.mkdir("parent_dir", job=10, case=42)
    ```

    The above code would create a directory `parent_dir/sub_dir_10/case_dir_42`.
    """
    wcard_sep: tuple[str, str] = ("<", ">")

    def __init__(self, path: str):
        self._path: str = str(path)
        self._count: defaultdict = defaultdict(int)
        self._wildcards: list[str] = self.find_wildcards()
        self._regex: str = self.wildcards_to_regex()
        self._groups: dict = {}

    @classmethod
    def wrap(cls, wildcard: str):
        return cls.wcard_sep[0] + wildcard + cls.wcard_sep[1]

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, p: str):
        self.__init__(p)

    def find_wildcards(self) -> list[str]:
        path = self.path
        start, stop = WildcardPath.wcard_sep
        wildcards = re.findall(f"{start}([^{start}{stop}]+){stop}", path)
        for w in wildcards:
            self._count[w] += 1

        wildcards = list(set(wildcards))

        self._groups = {}
        for w in wildcards:
            self._groups[w] = [f"{w}_{i}" for i in range(self._count[w])]

        return wildcards

    def wildcards_to_regex(self) -> str:
        """Replace wildcards in self.path with regex patterns.

        Regex named groups are used, so that the wildcard values can be
        later retrieved (see `get_matching_paths_and_values()`).
        """
        re_path = self.path
        start, stop = WildcardPath.wcard_sep

        for wname in self._wildcards:
            wcard = self.wrap(wname)
            groups = self._groups[wname]

            for gr in groups:
                re_path = re_path.replace(wcard, f"(?P{start}{gr}{stop}\\d+)", 1)
        re_path = ".*" + re_path + "/*$"
        return re_path

    def get_matching_paths_and_values(self, parent: str) -> dict[str, dict[str, int]]:
        """Return matching paths w.r.t. to parent and found wildcard values.

        For example, for the following directory structure:
        - parent_dir
            - sub_dir_0
            - sub_dir_1
                - file_1_0.csv
                - file_1_1.csv

        The output for this method would be:
        ```python
        >>> wp = WildcardPath("sub_dir_<job>/file_<job>_<step>.csv")
        >>> wp.get_matching_paths_and_values("parent_dir")
        {
            "parent_dir/sub_dir_1/file_1_0.csv": {"job": 1, "step": 0},
            "parent_dir/sub_dir_1/file_1_1.csv": {"job": 1, "step": 1},
        }
        ```
        """
        paths = {}
        regex = re.compile(self._regex)

        for f in Path(parent).glob("**/*"):
            f = str(f)
            match = regex.match(f)
            if match:
                paths[f] = {}
                for gr, val in match.groupdict().items():
                    wname = re.sub(r"_\d+$", "", gr)
                    if wname not in paths[f]:
                        paths[f][wname] = int(val)
                    else:
                        assert int(val) == paths[f][wname], \
                            f"Multiple values for one wildcard in a path are not allowed: {f}"

        return paths

    def get_matching_paths(self, parent) -> list[str]:
        """Same as `get_matching_paths_and_values()` but returns only the paths."""
        path_dict = self.get_matching_paths_and_values(parent)
        return list(path_dict.keys())

    def mkdir(self, parent: str, **kwargs) -> None:
        """Make directory replacing all wildcards with `kwargs`.

        The directory is created using `Path.mkdir(parents=True, exist_ok=True)`.
        If no wildcards are in the path, `kwargs` should be empty.
        Otherwise, the number of items in `kwargs` should match the number of wildcards
        in `self.path`.
        """
        path = None

        if len(self._wildcards) > 0:
            if len(kwargs.keys()) != len(self._wildcards):
                raise ValueError(f"Number of wildcards and provided arguments does not match")

            path = self.path
            for k, v in kwargs.items():
                if k not in self._wildcards:
                    raise KeyError(f"{k} not in wildcards: {self._wildcards}")

                path = path.replace(self.wrap(k), str(v))

            assert path is not None
            (Path(parent) / path).mkdir(parents=True, exist_ok=True)

        else:
            path = self.path
            assert path is not None
            (Path(parent) / path).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Example
    import building3d.simulators.rays.config as config
    project_dir = "tmp/parallel/"

    wp = WildcardPath(config.JOB_DIR)
    print(wp.get_matching_paths_and_values(project_dir))

    wp.path = config.JOB_HIT_CSV
    print(wp.get_matching_paths_and_values(project_dir))

    wp.path = config.JOB_STATE_DIR
    print(wp.get_matching_paths_and_values(project_dir))

    wp.path = config.JOB_LOG_FILE
    print(wp.get_matching_paths_and_values(project_dir))

    wp.path = "parallel"
    print(wp.get_matching_paths_and_values("tmp"))

    wp.path = "test_<number>/dir_<other>"
    print(wp.get_matching_paths_and_values("tmp"))
    wp.mkdir("tmp", number=99, other=666)
