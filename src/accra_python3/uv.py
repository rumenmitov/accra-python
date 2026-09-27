import subprocess
from typing import override

from accra_language import (
    AccraBuildError,
    AccraError,
    AccraInstallError,
    AccraResult,
    Config,
    DependencySpec,
    DockerfileInstruction,
    EnvironmentManager,
    EnvironmentManagerSpec,
)

from . import utils


class Uv(EnvironmentManager):
    def __init__(self):
        spec = EnvironmentManagerSpec(
            name="uv",
            version="0.12",
            default_language_version="3.14",
            supported_manifests={},
        )
        super().__init(spec)

    @override
    def _get_supported_language_versions_from_code(
        self, config: Config | None = None
    ) -> set[str] | AccraError | None:
        cfg = config or self.spec.config

        return utils.get_supported_python_versions_from_code(cfg)

    @override
    def _setup_environment(self, config: Config | None = None) -> AccraResult:
        cfg = config or self.spec.config

        uv_sync_result = subprocess.run(
            ["uv", "sync"],
            check=False,
            capture_output=True,
            text=True,
            **cfg.dump_model(),
        )

        if uv_sync_result.returncode != 0:
            return AccraBuildError(message="uv sync failed to setup environment")

        return [DockerfileInstruction("RUN uv sync")]

    @override
    def install(self, config: Config | None = None) -> AccraResult:
        cfg = config or self.spec.config

        curl_result = subprocess.run(
            ["curl", "-LsSf", "https://astral.sh/uv/install.sh"],
            check=False,
            capture_output=True,
            text=True,
            **cfg.dump_model(),
        )

        if curl_result.returncode != 0:
            return AccraInstallError(
                message=f"could not install environment manager: {self.name}-{self.version}"
            )

        shell_result = subprocess.run(
            ["sh"],
            stdin=curl_result.stdout,
            check=False,
            capture_output=True,
            text=True,
            **cfg.dump_model(),
        )

        if shell_result.returncode != 0:
            return AccraInstallError(
                message=f"could not install environment manager: {self.name}-{self.version}"
            )

        return [
            DockerfileInstruction(
                "RUN curl -LsSf https://astral.sh/uv/install.sh | sh"
            ),
        ]

    @override
    def install_language(
        self, language_version: str, config: Config | None = None
    ) -> AccraResult:
        cfg = config or self.spec.config

        pyenv_result = subprocess.run(
            ["pyenv", "install", language_version],
            check=False,
            capture_output=True,
            text=True,
            **cfg.dump_model(),
        )

        if pyenv_result.returncode != 0:
            return AccraInstallError(
                message=f"pyenv could not install python3 version: {language_version}"
            )

        return [
            DockerfileInstruction(f"RUN pyenv install {language_version}"),
        ]

    @override
    def install_dependency(
        self, dependency: DependencySpec, config: Config | None = None
    ) -> AccraResult:
        cfg = config or self.spec.config

        install_result = subprocess.run(
            ["uv", "add", dependency.name + dependency.version],
            check=False,
            capture_output=True,
            text=True,
            **cfg.dump_model(),
        )

        if install_result.returncode != 0:
            return AccraInstallError(
                message=f"{self.name} could not install dependency: {dependency.name + dependency.version}"
            )

        return [
            DockerfileInstruction(f"RUN uv add {dependency.name + dependency.version}"),
        ]
