import os
import re
from collections import defaultdict
from collections import namedtuple
from pathlib import Path
from typing import NamedTuple


class WildcardPath:
    """Custom path class which allows to use wildcards which can be read or replaced with numbers."""

    wcard_sep: tuple[str, str] = ("<", ">")

    def __init__(self, path: str):
        self._path: str = str(path)
        self._count: defaultdict = defaultdict(int)
        self._wildcards: list[str] = self._find_wildcards()
        self._regex: str = self._wildcards_to_regex()
        self._groups: dict = {}
        self.Case = namedtuple("Case", self._wildcards)

    @classmethod
    def wrap(cls, wildcard: str):
        return cls.wcard_sep[0] + wildcard + cls.wcard_sep[1]

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, p: str):
        self.__init__(p)

    def get_matching_paths_dict_values(self, parent: str) -> dict[str, dict[str, int]]:
        """Return a dict with paths as keys and dicts with wildcard names and values as keys.

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
                        assert (
                            int(val) == paths[f][wname]
                        ), f"Multiple values for one wildcard in a path are not allowed: {f}"
        return paths

    def get_matching_paths_namedtuple_keys(self, parent: str) -> dict[NamedTuple, str]:
        """Return a dict with named tuples as keys and paths as values.

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
            Case(job=1, step=0): "parent_dir/sub_dir_1/file_1_0.csv",
            Case(job=1, step=1): "parent_dir/sub_dir_1/file_1_1.csv",
        }

        ```
        """
        paths_dict_vals = self.get_matching_paths_dict_values(parent)
        paths = self._to_dict_with_namedtuple_keys(paths_dict_vals)

        return paths

    def get_matching_paths(self, parent, **kwargs) -> list[str]:
        """Return matching paths as a list of strings.

        Additional filtering is possible by providing specific wildcard values in `kwargs`.
        """
        path_dict = self.get_matching_paths_dict_values(parent)

        if len(kwargs.items()) == 0:
            paths = list(path_dict.keys())
        else:
            paths = []

            for p, wd in path_dict.items():
                num_matching = 0
                for wcard, val in wd.items():
                    for k, v in kwargs.items():
                        if k == wcard and v == val:
                            num_matching += 1

                if num_matching == len(kwargs.items()):
                    paths.append(p)

        return paths

    def fill(self, parent="", **kwargs) -> str:
        """Fill wildcards in the path with provided values.

        This method replaces all wildcards in the path with the values provided
        in kwargs. If a parent directory is specified, it is prepended to the
        resulting path.

        Args:
            parent (str, optional): Parent directory to prepend to the path.
                Defaults to an empty string.
            **kwargs: Keyword arguments where keys are wildcard names and values
                are their replacements.

        Returns:
            str: The path with all wildcards replaced by their corresponding
                values.

        Raises:
            ValueError: If the number of provided kwargs doesn't match the
                number of wildcards in the path.
            KeyError: If a provided kwarg doesn't correspond to any wildcard in
                the path.

        Example:
            >>> wp = WildcardPath("sub_dir_<job>/file_<step>.csv")
            >>> wp.fill(parent="data", job=5, step=2)
            'data/sub_dir_5/file_2.csv'
        """
        path = self.path

        if len(kwargs.keys()) != len(self._wildcards):
            raise ValueError(
                f"Number of wildcards and provided arguments does not match"
            )

        for k, v in kwargs.items():
            if k not in self._wildcards:
                raise KeyError(f"{k} not in wildcards: {self._wildcards}")

            path = path.replace(self.wrap(k), str(v))

        if len(parent) > 0:
            path = os.path.join(parent, path)
        return path

    def mkdir(self, parent: str, **kwargs) -> str:
        """Make directory replacing all wildcards with `kwargs`.

        The directory is created using `Path.mkdir(parents=True, exist_ok=True)`.
        If no wildcards are in the path, `kwargs` should be empty.
        Otherwise, the number of items in `kwargs` should match the number of wildcards
        in `self.path`.

        ```python
        >>> wp = WildcardPath("sub_dir_<job>/case_dir_<case>")
        >>> wp.mkdir("parent_dir", job=10, case=42)

        ```

        The above code would create a directory `parent_dir/sub_dir_10/case_dir_42`.

        Args:
            parent: parent directory for self.path
            kwargs: keyword arguments mapped to wildcards

        Return:
            absolute path to the created directory
        """
        path = self.fill(parent=parent, **kwargs)
        abs_path = Path(path)
        abs_path.mkdir(parents=True, exist_ok=True)

        return str(abs_path)

    def _find_wildcards(self) -> list[str]:
        """Find wildcards within the path string and return as a list."""
        path = self.path
        start, stop = WildcardPath.wcard_sep
        wildcards = re.findall(f"{start}([^{start}{stop}]+){stop}", path)
        for w in wildcards:
            self._count[w] += 1

        wildcards = sorted(list(set(wildcards)))

        self._groups = {}
        for w in wildcards:
            self._groups[w] = [f"{w}_{i}" for i in range(self._count[w])]

        return wildcards

    def _wildcards_to_regex(self) -> str:
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

    def _to_dict_with_namedtuple_keys(
        self, d: dict[str, dict[str, int]]
    ) -> dict[NamedTuple, str]:
        """Convert a dictionary with string keys to a dictionary with namedtuple keys.

        This method takes a dictionary where the keys are strings (file paths) and
        the values are dictionaries containing wildcard names and their corresponding
        integer values. It returns a new dictionary where the keys are namedtuples
        (instances of self.Case) created from the wildcard dictionaries, and the
        values are the original file paths.

        Args:
            d (dict[str, dict[str, int]]): A dictionary with string keys (file paths)
                and dictionary values (wildcard name-value pairs).

        Returns:
            dict[NamedTuple, str]: A dictionary with namedtuple keys (instances of
                self.Case) and string values (file paths).
        """
        dnew = {}
        for p, wd in d.items():
            s = self.Case(**wd)
            dnew[s] = p
        return dnew
