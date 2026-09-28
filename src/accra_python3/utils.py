import subprocess
from functools import cache
from pathlib import Path

from accra_language import AccraError, Config
from packaging.specifiers import SpecifierSet
from packaging.version import Version


@cache
def get_supported_python_versions_from_code(config: Config) -> set[str] | AccraError:
    min_minor_version: int = 0

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

    min_minor_version = int(py3_version.split(".")[1]) or min_minor_version

    return get_python_minor_versions(min_minor_version)


@cache
def get_python_minor_versions(min_minor_version: int) -> set[str]:
    MAX_MINOR_VERSION = 13

    all_versions: set[str] = {
        f"3.{i}" for i in range(min_minor_version, MAX_MINOR_VERSION + 1)
    }

    parsed_versions: set[str] = {
        v for v in all_versions if SpecifierSet(">=3.0").contains(Version(v))
    }

    return parsed_versions
