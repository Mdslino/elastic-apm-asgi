import functools
import urllib
from json import JSONDecodeError
from typing import Dict

import elasticapm
from starlette.requests import Request
from starlette.types import ASGIApp, Scope, Receive, Send


class SentryMiddleware:
    def __init__(self, app: ASGIApp, service_name: str, elastic_config: Dict = None, log_request_info=True,
                 log_request_data=True):
        if elastic_config is None:
            elastic_config = {}
        self.apm_client = elasticapm.Client({'SERVICE_NAME': service_name}, **elastic_config or {})
        self.app = app
        self.transaction = {}
        self.log_request_info = log_request_info
        self.log_request_data = log_request_data

    def __call__(self, scope: Scope):
        return functools.partial(self.asgi, asgi_scope=scope)

    async def asgi(self, receive: Receive, send: Send, asgi_scope: Scope):
        try:
            inner = self.app(asgi_scope)
            await self.make_transaction_scope(asgi_scope, receive)
            await inner(receive, send)
            self.apm_client.end_transaction(self.transaction.get('path', 'lifespan'))
        except Exception as exc:
            self.apm_client.capture_exception()
            raise exc from None

    async def make_transaction_scope(self, asgi_scope: Scope, receive: Receive):
        if asgi_scope['type'] != 'lifespan':
            context = {}
            self.transaction['url'] = self.get_url(asgi_scope)
            self.transaction['path'] = self.get_transaction(asgi_scope)
            self.transaction['headers'] = self.get_headers(asgi_scope)
            self.transaction['query'] = self.get_query(asgi_scope)
            self.apm_client.begin_transaction('request')
            if self.log_request_info:
                context.update(**{'headers': self.transaction.get('headers'),
                                  'url': self.transaction.get('url'),
                                  'path': self.transaction.get('path'),
                                  'query': self.transaction.get('query')})
            if self.log_request_data:
                request_data = await self.get_request_data(asgi_scope, receive)
                context.update(**{'body': request_data})
            elasticapm.set_custom_context(context)
            elasticapm.instrument()

    async def get_request_data(self, asgi_scope: Scope, receive: Receive):
        if asgi_scope["type"] in ("http", "websocket"):
            request = Request(asgi_scope, receive)
            try:
                request_data = await request.json()
                return request_data
            except JSONDecodeError:
                request_data = await request.body()
                return request_data.decode()

    def get_url(self, scope: Scope):
        """
        Extract URL from the ASGI scope, without also including the querystring.
        """
        scheme = scope.get("scheme", "http")
        server = scope.get("server", None)
        path = scope.get("root_path", "") + scope["path"]

        for key, value in scope["headers"]:
            if key == b"host":
                host_header = value.decode("latin-1")
                return "%s://%s%s" % (scheme, host_header, path)

        if server is not None:
            host, port = server
            default_port = {"http": 80, "https": 443, "ws": 80, "wss": 443}[scheme]
            if port != default_port:
                return "%s://%s:%s%s" % (scheme, host, port, path)
            return "%s://%s%s" % (scheme, host, path)
        return path

    def get_query(self, scope: Scope):
        """
        Extract querystring from the ASGI scope, in the format that the Sentry protocol expects.
        """
        return urllib.parse.unquote(scope["query_string"].decode("latin-1"))

    def get_headers(self, scope: Scope):
        """
        Extract headers from the ASGI scope, in the format that the Sentry protocol expects.
        """
        headers = {}
        for raw_key, raw_value in scope["headers"]:
            key = raw_key.decode("latin-1")
            value = raw_value.decode("latin-1")
            if key in headers:
                headers[key] = headers[key] + ", " + value
            else:
                headers[key] = value
        return headers

    def get_transaction(self, scope: Scope):
        """
        Return a transaction string to identify the routed endpoint.
        """
        return scope.get("endpoint") or scope.get("path")
