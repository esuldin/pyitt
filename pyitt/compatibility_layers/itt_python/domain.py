from pyitt.native import Domain as _Domain


def domain_create(name) -> _Domain:
    """
    Creates a domain with the given name.
    :param name: a name of the domain
    :return: a handle to the created domain with given name if the `name` is not None.
     Otherwise, returns handle to default domain.
    """
    return _Domain(name)
