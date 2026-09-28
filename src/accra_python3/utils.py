import subprocess
from functools import cache
from pathlib import Path

from accra_language import AccraError, Config
from packaging.specifiers import SpecifierSet
from packaging.version import Version


@cache
def get_supported_python_versions_from_code(config: Config) -> set[str] | AccraError:
    requires_python: str = "3"

    result = subprocess.run(
        ["vermin", "-f", "parsable", config.cwd or Path(".")],
        check=False,
        capture_output=True,
        text=True,
        **config.model_dump(),
    )

    if result.returncode != 0:
        # NOTE this could be just vermin failing to find any Python
        # code, so we return an empty set
        return set()

    lines = result.stdout.splitlines()
    if not lines:
        return set()

    summary = [x for x in lines[-1].strip().split(":") if x]
    py3_version = summary[-1].strip("~")

    if py3_version.startswith("!"):
        return set()

    requires_python = py3_version or requires_python
    requires_python = ">=" + requires_python

    return get_python_minor_versions(requires_python)


@cache
def get_python_minor_versions(requires_python: str) -> set[str]:
    MIN_MINOR_VERSION = 0
    MAX_MINOR_VERSION = 13

    all_versions: set[str] = {
        f"3.{i}" for i in range(MIN_MINOR_VERSION, MAX_MINOR_VERSION + 1)
    }

    parsed_versions: set[str] = {
        v for v in all_versions if SpecifierSet(requires_python).contains(Version(v))
    }

    return parsed_versions
