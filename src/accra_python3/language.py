from typing import override

from accra_language import (
    AccraError,
    Config,
    Language,
    LanguageSpec,
)
from uv import Uv

from . import utils


class Python3(Language):
    def __init__(self):
        spec = LanguageSpec(name="python3", version="3", supported_env_managers={Uv()})
        super().__init__(spec)

    @override
    def detect(self, config: Config | None = None) -> bool:
        cfg = config or self.spec.config

        result: set[str] | AccraError = utils.get_supported_python_versions_from_code(
            cfg
        )
        match result:
            case set():
                return bool(result)

            case AccraError():
                return result
