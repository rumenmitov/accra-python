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

from .adhoc import Adhoc
from .pyproject_toml import Pyproject_toml


class Uv(EnvironmentManager):
    def __init__(self, config: Config):
        spec = EnvironmentManagerSpec(
            name="uv",
            version="0.12",
            default_language_version="3.14",
            supported_manifests={Adhoc(config), Pyproject_toml(config)},
            config=config,
        )
        super().__init__(spec)

        self.is_pyproject_present: bool = bool(
            [
                manifest
                for manifest in self.present_manifests
                if isinstance(manifest, Pyproject_toml)
            ]
        )

    def _install_uv(self) -> AccraError | None:
        curl_result = subprocess.run(
            ["curl", "-LsSf", "https://astral.sh/uv/install.sh"],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if curl_result.returncode != 0:
            return AccraInstallError(
                message=f"could not install environment manager: {self.spec.name}-{self.spec.version}"
            )

        shell_result = subprocess.run(
            ["sh"],
            stdin=curl_result.stdout,
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if shell_result.returncode != 0:
            return AccraInstallError(
                message=f"could not install environment manager: {self.spec.name}-{self.spec.version}"
            )

        return None

    def _uv_pyproject_setup(self) -> AccraResult:
        uv_sync_result = subprocess.run(
            ["uv", "sync"],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if uv_sync_result.returncode != 0:
            return AccraBuildError(message="uv sync failed")

        return [DockerfileInstruction("RUN uv sync")]

    def _uv_non_pyproject_setup(self) -> AccraResult:
        uv_venv_result = subprocess.run(
            ["uv", "venv"],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if uv_venv_result.returncode != 0:
            return AccraBuildError(message="uv venv failed")

        return [DockerfileInstruction("RUN uv venv")]

    @override
    def setup(self) -> AccraResult:
        dockerfile: list[DockerfileInstruction] = []

        language_version: str | AccraError = self.select_language_version()
        if isinstance(language_version, AccraError):
            return language_version

        # install python
        pyenv_result = subprocess.run(
            ["pyenv", "install", "--skip-existing", language_version],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if pyenv_result.returncode != 0:
            return AccraInstallError(
                message=f"pyenv could not install python3 version: {language_version}"
            )

        dockerfile.append(
            DockerfileInstruction(
                f"RUN pyenv install --skip-existing {language_version}"
            ),
        )

        # install uv (if not already installed)
        uv_version_result = subprocess.run(
            ["uv", "--version"],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if uv_version_result.returncode != 0:
            uv_install_error = self._install_uv()
            if uv_install_error:
                return uv_install_error

        dockerfile.append(
            DockerfileInstruction("RUN curl -LsSf https://astral.sh/uv/install.sh | sh")
        )

        # setup uv
        setup_result: AccraResult = (
            self._uv_pyproject_setup()
            if self.is_pyproject_present
            else self._uv_non_pyproject_setup()
        )
        if isinstance(setup_result, AccraError):
            return setup_result

        dockerfile.extend(setup_result)

        return dockerfile

    def _install_pyproject_dependency(self, dependency: DependencySpec) -> AccraResult:
        install_result = subprocess.run(
            ["uv", "add", dependency.name + dependency.version],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if install_result.returncode != 0:
            return AccraInstallError(
                message=f"{self.spec.name} could not install dependency: {dependency.name + dependency.version}"
            )

        return [
            DockerfileInstruction(f"RUN uv add {dependency.name + dependency.version}")
        ]

    def _install_non_pyproject_dependency(
        self, dependency: DependencySpec
    ) -> AccraResult:
        install_result = subprocess.run(
            ["uv", "pip", "install", dependency.name + dependency.version],
            check=False,
            capture_output=True,
            text=True,
            **self.spec.config.model_dump(),
        )

        if install_result.returncode != 0:
            return AccraInstallError(
                message=f"{self.spec.name} could not install dependency: {dependency.name + dependency.version}"
            )

        return [
            DockerfileInstruction(
                f"RUN uv pip install {dependency.name + dependency.version}"
            )
        ]

    @override
    def _install_dependency(self, dependency: DependencySpec) -> AccraResult:
        result: AccraResult = (
            self._install_pyproject_dependency(dependency)
            if self.is_pyproject_present
            else self._install_non_pyproject_dependency(dependency)
        )

        return result
