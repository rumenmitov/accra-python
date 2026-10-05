import shutil
from pathlib import Path

from accra_language import AccraError, Config, DependencySpec

from accra_python import Setup_cfg


def test_setupcfg():
    correct_dependencies: set[DependencySpec] = {
        DependencySpec(name="requests", version=""),
        DependencySpec(name="numpy", version=""),
        DependencySpec(name="click", version=""),
    }

    project_dir = Path(__file__).resolve().parent / Path("fixtures/setup_cfg-project")
    tmp_dir = Path("/tmp/setup_cfg-project")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    shutil.copytree(project_dir, tmp_dir)

    try:
        config = Config(cwd=tmp_dir)
        setupcfg = Setup_cfg(config)

        assert setupcfg.detect()

        deps: set[DependencySpec] | AccraError = setupcfg.extract_dependencies()
        assert not isinstance(deps, AccraError)

        assert deps == correct_dependencies

    finally:
        shutil.rmtree(tmp_dir)
