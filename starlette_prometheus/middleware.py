import functools


class SentryMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, scope):
        return functools.partial(self.asgi, scope=scope)

    async def asgi(self, receive, send, scope):
        pass
