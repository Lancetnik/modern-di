import datetime

from modern_di import Container, Scope, resolvers


def context_adapter_function(*, now: datetime.datetime, **_: object) -> datetime.datetime:
    return now


context_adapter = resolvers.ContextAdapter(Scope.APP, context_adapter_function)


async def test_context_adapter() -> None:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    async with Container(scope=Scope.APP, context={"now": now}) as app_container:
        instance1 = await context_adapter.async_resolve(app_container)
        instance2 = context_adapter.sync_resolve(app_container)
        assert instance1 is instance2 is now


async def test_context_adapter_override() -> None:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    async with Container(scope=Scope.APP, context={"now": now}) as app_container:
        instance1 = await context_adapter.async_resolve(app_container)
        context_adapter.override(datetime.datetime.now(tz=datetime.timezone.utc), container=app_container)
        instance2 = context_adapter.sync_resolve(app_container)
        assert instance1 is now
        assert instance2 is not now
