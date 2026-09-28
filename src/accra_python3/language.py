from typing import override

from accra_language import (
    AccraError,
    Config,
    Language,
    LanguageSpec,
)

from . import utils
from .uv import Uv


class Python3(Language):
    def __init__(self, config: Config):
        spec = LanguageSpec(
            name="python3",
            version="3",
            supported_env_managers={Uv(config)},
            config=config,
        )
        super().__init__(spec)

    @override
    def detect(self) -> bool:
        result: set[str] | AccraError = utils.get_supported_python_versions_from_code(
            self.spec.config
        )

        match result:
            case set():
                return bool(result)

            case AccraError():
                return result
