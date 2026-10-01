import shutil
from pathlib import Path

import pytest
from accra_language import AccraError, AccraResult, Config, DockerfileInstruction

from accra_python3 import Python3


def test_adhoc_package_resolution():
    correct_dockerfile: list[DockerfileInstruction] = [
        "RUN pyenv install --skip-existing 3.10",
        "RUN curl -LsSf https://astral.sh/uv/install.sh | sh",
        "RUN uv venv",
        "RUN uv pip install PyYAML",
    ]

    project_dir = Path(__file__).resolve().parent / Path(
        "fixtures/adhoc-module-project"
    )
    tmp_dir = Path("/tmp/adhoc-module-project")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    shutil.copytree(project_dir, tmp_dir)

    try:
        config = Config(cwd=tmp_dir)
        python3 = Python3(config)

        assert python3.detect()

        result: AccraResult = python3.build()
        assert result

        match result:
            case list():
                assert result == correct_dockerfile

            case AccraError():
                pytest.fail(result.message)

    finally:
        shutil.rmtree(tmp_dir)
