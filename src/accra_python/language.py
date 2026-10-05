from accra_language import (
    Config,
    Language,
    LanguageSpec,
)

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
