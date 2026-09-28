import shutil
from pathlib import Path

import pytest
from accra_language import AccraError, AccraResult, Config, DockerfileInstruction

from accra_python3 import Python3


def test_uv():
    correct_dockerfile: list[DockerfileInstruction] = [
        "RUN pyenv install --skip-existing 3.14",
        "RUN curl -LsSf https://astral.sh/uv/install.sh | sh",
        "RUN uv sync",
    ]

    uv_sample_project_dir = Path(__file__).resolve().parent / Path(
        "fixtures/uv-sample-project"
    )
    tmp_dir = Path("/tmp/uv-sample-project")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    shutil.copytree(uv_sample_project_dir, tmp_dir)

    try:
        config = Config(cwd=Path("."))
        python3 = Python3(config)

        assert python3.detect()

        result: AccraResult = python3.build()

        match result:
            case list():
                assert result == correct_dockerfile

            case AccraError():
                pytest.fail(result.message)

    finally:
        shutil.rmtree(tmp_dir)
