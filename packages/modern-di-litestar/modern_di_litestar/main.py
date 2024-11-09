import dataclasses
import enum
import typing

import litestar
from litestar.di import Provide
from modern_di import Container, providers
from modern_di import Scope as DIScope


T_co = typing.TypeVar("T_co", covariant=True)


def setup_di(app: litestar.Litestar, scope: enum.IntEnum = DIScope.APP) -> Container:
    app.dependencies["request_di_container"] = Provide(build_di_container)
    app.state.di_container = Container(scope=scope)
    return app.state.di_container


def fetch_di_container(app: litestar.Litestar) -> Container:
    return typing.cast(Container, app.state.di_container)


async def build_di_container(
    request: litestar.Request[typing.Any, typing.Any, typing.Any],
) -> typing.AsyncIterator[Container]:
    scope = DIScope.REQUEST
    context = {"request": request}
    container: Container = fetch_di_container(request.app)
    async with container.build_child_container(context=context, scope=scope) as request_container:
        yield request_container


@dataclasses.dataclass(slots=True, frozen=True)
class Dependency(typing.Generic[T_co]):
    dependency: providers.AbstractProvider[T_co]

    async def __call__(self, request_di_container: Container) -> T_co:
        return await self.dependency.async_resolve(request_di_container)


def FromDI(dependency: providers.AbstractProvider[T_co], *, use_cache: bool = True) -> Provide:  # noqa: N802
    return Provide(dependency=Dependency(dependency), use_cache=use_cache)
