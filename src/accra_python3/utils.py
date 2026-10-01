from functools import cache

from packaging.specifiers import SpecifierSet
from packaging.version import Version


@cache
def get_python_minor_versions(requires_python: str) -> set[str]:
    MIN_MINOR_VERSION = 0
    MAX_MINOR_VERSION = 14

    all_versions: set[str] = {
        f"3.{i}" for i in range(MIN_MINOR_VERSION, MAX_MINOR_VERSION + 1)
    }

    parsed_versions: set[str] = {
        v for v in all_versions if SpecifierSet(requires_python).contains(Version(v))
    }

    return parsed_versions
