
from __future__ import absolute_import

import abc
import typing
from typing import Optional

import fastapi
import pydantic_settings
import asyncio
from abc import ABC
from typing import Protocol, runtime_checkable

@runtime_checkable
class Settings(Protocol):
    ...

class PluginError(Exception):
    pass


class PluginSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix='',
        use_enum_values=True
    )


class Plugin:
    DEFAULT_CONFIG_CLASS: Optional[Settings] = None

    def __init__(
            self,
            app: Optional[fastapi.FastAPI] = None,
            config: Optional[Settings] = None
    ):
        self._on_init()
        if app:
            asyncio.run(self.init_app(app, config))

    def __call__(self) -> typing.Any:
        return self._on_call()

    def _on_init(self) -> None:
        pass

#     def is_initialized(self) -> bool:
#         raise NotImplementedError('implement is_initialied()')

    @abc.abstractmethod
    async def _on_call(self) -> typing.Any:
        raise NotImplementedError('implement _on_call()')

    async def initialize(self, app: fastapi.FastAPI, config: Optional[Settings]=None):
        pass

    async def init_app(
            self,
            app: fastapi.FastAPI,
            config: Optional[Settings]=None,
            *args,
            **kwargs
    ) -> None:
        pass

    async def init(self):
        pass

    async def terminate(self, app: fastapi.FastAPI):
        pass