import shutil
from pathlib import Path

from accra_language import AccraError, Config, DependencySpec

from accra_python import Setup_py


def test_setuppy():
    correct_dependencies: set[DependencySpec] = {
        DependencySpec(name="requests", version=""),
        DependencySpec(name="numpy", version=""),
        DependencySpec(name="click", version=""),
    }

    project_dir = Path(__file__).resolve().parent / Path("fixtures/setup_py-project")
    tmp_dir = Path("/tmp/setup_py-project")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    shutil.copytree(project_dir, tmp_dir)

    try:
        config = Config(cwd=tmp_dir)
        setuppy = Setup_py(config)

        assert setuppy.detect()

        deps: set[DependencySpec] | AccraError = setuppy.extract_dependencies()
        assert not isinstance(deps, AccraError)

        assert deps == correct_dependencies

    finally:
        shutil.rmtree(tmp_dir)
