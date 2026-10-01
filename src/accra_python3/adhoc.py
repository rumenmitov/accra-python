import subprocess
from pathlib import Path
from typing import override

from accra_language import AccraError, Config, DependencySpec, Manifest, ManifestSpec

from . import utils


class Adhoc(Manifest):
    def __init__(self, config: Config):
        spec = ManifestSpec(name="adhoc", version="", config=config)
        super().__init__(spec)

    @override
    def detect(self) -> bool:
        return True

    @override
    def extract_dependencies(self) -> set[DependencySpec] | None:
        # TODO
        return None

    @override
    def get_supported_language_versions(self) -> set[str] | AccraError:
        requires_python: str = "3"

        result = subprocess.run(
            ["vermin", "-f", "parsable", self.spec.config.cwd or Path(".")],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if result.returncode != 0:
            # NOTE this is just vermin failing to find any Python
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

        return utils.get_python_minor_versions(requires_python)
