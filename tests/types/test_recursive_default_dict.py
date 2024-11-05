from building3d.types.recursive_default_dict import recursive_default_dict
from building3d.types.recursive_default_dict import recursive_default_dict_to_dict


def test_recursive_default_dict_basic():
    """Test basic nested dictionary creation and access."""
    d = recursive_default_dict()

    # Test setting nested values
    d['a']['b']['c'] = 1
    assert d['a']['b']['c'] == 1

    # Test accessing non-existent paths returns a new default dict
    result = d['x']['y']
    assert isinstance(result, type(d))
    assert len(result) == 0


def test_recursive_default_dict_to_dict():
    """Test conversion from recursive default dict to regular dict."""
    d = recursive_default_dict()

    # Set up some nested test data
    d['a']['b'] = 1
    d['x']['y'] = {'z': 2}

    # Convert to regular dict
    result = recursive_default_dict_to_dict(d)

    # Verify the structure and values
    assert isinstance(result, dict)
    assert result['a']['b'] == 1
    assert result['x']['y']['z'] == 2

    # Verify it's a regular dict all the way down
    assert isinstance(result['a'], dict)
    assert isinstance(result['x'], dict)
    assert isinstance(result['x']['y'], dict)


def test_recursive_default_dict_to_dict_empty():
    """Test conversion of empty recursive default dict."""
    d = recursive_default_dict()
    result = recursive_default_dict_to_dict(d)

    assert isinstance(result, dict)
    assert len(result) == 0
