from pyitt.native import PTRegion as _PTRegion


def pt_region_create(name) -> _PTRegion:
    """
    Creates a PT region with the given name.
    :param name: a name of the region
    :return: a PT region instance
    """
    return _PTRegion(name)


def pt_region_begin(region: _PTRegion) -> None:
    """
    Marks the beginning of the PT region.
    :param region: a PT region instance
    :return: None
    """
    region.begin()


def pt_region_end(region: _PTRegion) -> None:
    """
    Marks the end of the PT region.
    :param region: a PT region instance
    :return: None
    """
    region.end()
