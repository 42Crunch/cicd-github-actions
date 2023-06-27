from __future__ import annotations

import os
import json
import signal
import asyncio

from typing import List, Dict

from urllib.parse import urlparse, parse_qsl

from xliic_cli.helpers import print_prompt_message

try:
    import aiofiles

    from mitmproxy import http
    from mitmproxy.tools.main import mitmdump

    mitm_enabled = True
except ImportError:
    mitm_enabled = False


MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 10))


def signal_handler(signal, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGINT, signal_handler)


class HTTP:

    def __init__(self, **kwargs):
        self.url: str = kwargs.get("url")
        self.request_host: str = kwargs.get("request_host")
        self.request_path: str = kwargs.get("request_path")
        self.request_path_raw: str = kwargs.get("request_path_raw")
        self.request_query_params: str | None = kwargs.get("request_query_params")
        self.request_method: str = kwargs.get("request_method")
        self.request_headers: Dict[str, str] = kwargs.get("request_headers")
        self.request_cookies: Dict[str, str] = kwargs.get("request_cookies")
        self.request_body: str | None = kwargs.get("request_body")
        self.request_sequence: int = kwargs.get("request_sequence")
        self.request_source_ipv4: str = kwargs.get("request_source_ipv4")
        self.request_source_ipv6: str = kwargs.get("request_source_ipv6")
        self.request_dest_ipv4: str = kwargs.get("request_dest_ipv4")
        self.request_dest_ipv6: str = kwargs.get("request_dest_ipv6")
        self.request_timestamp: float = kwargs.get("request_timestamp")
        self.request_http_version: str = kwargs.get("request_http_version")

        self.response_host: str = kwargs.get("response_host")
        self.response_code: int = kwargs.get("response_code")
        self.response_reason: str = kwargs.get("response_reason")
        self.response_headers: List[Dict[str, str]] = kwargs.get("response_headers")
        self.response_body: str | None = kwargs.get("response_body")
        self.response_sequence: int = kwargs.get("response_sequence")
        self.response_source_ipv4: str = kwargs.get("response_source_ipv4")
        self.response_source_ipv6: str = kwargs.get("response_source_ipv6")
        self.response_dest_ipv4: str = kwargs.get("response_dest_ipv4")
        self.response_dest_ipv6: str = kwargs.get("response_dest_ipv6")
        self.response_timestamp: float = kwargs.get("response_timestamp")
        self.response_http_version: str = kwargs.get("response_http_version")

    @classmethod
    def from_dict(cls, obj: dict) -> HTTP:

        def ifind_in_dict(_dict_value: dict, _key: str) -> str or None:
            """
            Case-insensitive finder in dictionary keys
            """
            if not _dict_value:
                return None

            key_lower = _key.lower()

            for k, v in _dict_value.items():

                if k.lower() == key_lower:
                    return v

            return None

        request_path_raw = obj.get("request_path") or "/"
        parsed_query_path = urlparse(request_path_raw)

        if found := ifind_in_dict(obj.get("request_headers"), "Cookie"):
            request_cookies = dict(tuple(x.split("=")) for x in found.split(";"))
        else:
            request_cookies = {}

        # Convert query params to dict
        if parsed_query_path.query:
            query_params = dict(parse_qsl(parsed_query_path.query))
        else:
            query_params = None

        return cls(
            url=obj.get("url"),
            request_host=obj.get("request_host") or "localhost",
            request_path=parsed_query_path.path,
            request_path_raw=request_path_raw,
            request_query_params=query_params,
            request_method=obj.get("request_method"),
            request_headers=obj.get("request_headers"),
            request_cookies=request_cookies,
            request_body=obj.get("request_body"),
            request_source_ipv4=obj.get("request_source_ipv4"),
            request_source_ipv6=obj.get("request_source_ipv6"),
            request_dest_ipv4=obj.get("request_dest_ipv4"),
            request_dest_ipv6=obj.get("request_dest_ipv6"),
            request_timestamp=obj.get("request_timestamp"),
            request_sequence=obj.get("request_sequence"),
            request_http_version=obj.get("request_http_version"),

            response_host=obj.get("response_host") or "localhost",
            response_code=obj.get("response_code"),
            response_reason=obj.get("response_reason"),
            response_headers=obj.get("response_headers"),
            response_body=obj.get("response_body"),
            response_source_ipv4=obj.get("response_source_ipv4"),
            response_source_ipv6=obj.get("response_source_ipv6"),
            response_dest_ipv4=obj.get("response_dest_ipv4"),
            response_dest_ipv6=obj.get("response_dest_ipv6"),
            response_timestamp=obj.get("response_timestamp"),
            response_sequence=obj.get("response_sequence"),
            response_http_version=obj.get("response_http_version")
        )


async def record_http_call(http_call: HTTP) -> None:
    file_path = os.environ.get("PROXY_FILE_PATH")

    print_prompt_message(f"Received request from {http_call.url}")

    async with aiofiles.open(file_path, mode='a') as f:
        await f.write(json.dumps(http_call, default=lambda o: o.__dict__) + "\n")


class HorusMITMProxyAddon:

    def __init__(self):
        self._workers = []
        self._queue = asyncio.Queue()
        self.initialized = False

    async def start_workers(self, workers: int = 1):
        """
        Start background workers
        """
        self.initialized = True

        for i in range(workers):
            worker = asyncio.create_task(self.background_record_http())
            self._workers.append(worker)

    async def background_record_http(self):
        """
        Background task to record HTTP requests
        """

        while True:
            data: HTTP = await self._queue.get()

            await record_http_call(data)

            self._queue.task_done()

    async def record_http(self, data: HTTP):
        """
        Record an HTTP request
        """
        await self._queue.put(data)


# ------------------------------------------------------------------------------------------------------------------
# MITM Addon
# ------------------------------------------------------------------------------------------------------------------
class Horus:

    def __init__(self):
        self.horus_mitm = HorusMITMProxyAddon()

    async def response(self, flow: http.HTTPFlow):
        if not self.horus_mitm.initialized:
            await self.horus_mitm.start_workers(MAX_WORKERS)

        await self.horus_mitm.record_http(self.flow_to_http(flow))

    def flow_to_http(self, flow: http.HTTPFlow) -> HTTP:
        _request = flow.request
        _response = flow.response

        if getattr(_request, "content", None):
            request_content = _request.content.decode("utf-8")
        else:
            request_content = None

        if getattr(_response, "content", None):
            response_content = _response.content.decode("utf-8")
        else:
            response_content = None

        try:
            request_http_version = _request.http_version.split("/")[1]
        except:
            request_http_version = "1.1"

        try:
            response_http_version = _response.http_version.split("/")[1]
        except:
            response_http_version = "1.1"

        try:
            client_addr, client_port, *_ = flow.client_conn.address
        except TypeError:
            client_addr, client_port = "127.0.0.1", ""

        try:
            server_addr, server_port, *_ = flow.server_conn.address
        except TypeError:
            server_addr, server_port = "127.0.0.1", ""

        return HTTP.from_dict(dict(
            url=_request.url,
            request_host=_request.host,
            request_path=_request.path,
            request_method=_request.method,
            request_headers=dict(_request.headers),
            request_body=request_content,
            request_source_ipv4=f"127.0.0.1:{client_port}",
            request_source_ipv6=f"::1:{client_port}",
            request_dest_ipv4=f"{server_addr}:{server_port}",
            request_dest_ipv6=f"{server_addr}:{server_port}",
            request_timestamp=_request.timestamp_end,
            request_sequence=_request.timestamp_start,
            request_http_version=request_http_version,

            response_host=_request.host,
            response_code=_response.status_code,
            response_reason=_response.reason,
            response_headers=dict(_response.headers),
            response_body=response_content,
            response_source_ipv4=f"127.0.0.1:{client_port}",
            response_source_ipv6=f"::1:{client_port}",
            response_dest_ipv4=f"{server_addr}:{server_port}",
            response_dest_ipv6=f"{server_addr}:{server_port}",
            response_timestamp=_response.timestamp_start,
            response_sequence=_response.timestamp_start,
            response_http_version=response_http_version,
        ))


addons = [Horus()]


def start_proxy(port: int):
    if mitm_enabled:
        mitmdump(["-s", __file__, "-p", str(port), "--quiet"])
    else:
        raise Exception("proxy is not installed, use [proxy] option to install it")
