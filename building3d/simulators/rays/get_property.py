import logging

from building3d.geom.paths import PATH_SEP


logger = logging.getLogger(__name__)


def get_property(target_surface: str, prop_name: str, property_dict: dict) -> float:
    """Get property for target surface from the property dict.

    If the target surface path is not in the property dict keys,
    a parent object is found and its property value retrieved.
    Then the path to the target surface is added to the property dict
    so that it can be directly retrieved in the future.

    Args:
        target_surface: path to the target surface (polygon or subpolygon)
        prop_name: property name, e.g. "absorption"
        property_dict: mapping between objects and property values

    Return:
        float
    """
    logger.debug(f"Get {prop_name} property for {target_surface}")

    assert prop_name in property_dict

    target_split = target_surface.split(PATH_SEP)
    if target_split[-1] == "":
        raise ValueError("Trailing path separator is not allowed")

    # target path length needs to be either 4 (polygon) or 5 (subpolygon)
    if not (len(target_split) in (4, 5)):
        raise ValueError("Too long or too short object path")

    if target_surface in property_dict[prop_name]:
        # This target surface is already in the property dict and can be returned
        return property_dict[prop_name][target_surface]
    else:
        # Need to find the parent object and update the property_dict to speed up future queries
        parent = find_parent(target_surface, candidates=list(property_dict[prop_name].keys()))
        prop_val = property_dict[prop_name][parent]
        property_dict[prop_name][target_surface] = prop_val
        return property_dict[prop_name][target_surface]


def find_parent(obj: str, candidates: list[str]):
    """Find parent object from the list of candidate object paths."""
    logger.debug(f"Find parent for {obj} in {candidates}")

    if len(obj) < min([len(x) for x in candidates]):
        raise ValueError(
            f"Object path ({obj}) is shorter than all parent candidate paths: {candidates}"
        )

    # Remove candidates which are longer than object path - they cannot be parents
    # Remove candidates which obviously do not match (check substrings)
    candidates = [x for x in candidates if ((len(x) < len(obj)) and (x in obj))]

    if len(candidates) == 0:
        raise ValueError(f"No parent found for {obj} within filtered candidates: {candidates}")
    elif len(candidates) > 1:
        parent = get_longest_string(candidates)
    else:
        parent = candidates[0]

    logger.debug(f"Parent found: {parent}")
    return parent


def get_longest_string(lst: list[str]):
    """Return the longest string from the list."""
    s = lst.pop()
    while len(lst) > 0:
        nxt = lst.pop()
        if len(nxt) > len(s):
            s = nxt
    return s
