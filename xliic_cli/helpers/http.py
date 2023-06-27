import requests

from .config_file import get_token, get_url


def _make_http_headers(headers: dict = None, use_token: bool = True) -> dict:
    headers = headers or {}

    if use_token:
        token = get_token()
        if not token:
            raise Exception("Error, you are not logged in")
        headers["Authorization"] = token

    return headers


def http_get(path: str, url: str = None, headers: dict = None, params: dict = None, use_token: bool = True, **kwargs):
    headers = _make_http_headers(headers=headers, use_token=use_token)

    if not url:
        url = f"{get_url()}{path}"
    else:
        url = f"{url}{path}"

    return requests.get(url=url, headers=headers, params=params, **kwargs)


def http_post(path: str, url: str = None, req_body: dict = None, headers: dict = None, params: dict = None, use_token: bool = True, **kwargs):
    headers = _make_http_headers(headers=headers, use_token=use_token)

    if not url:
        url = f"{get_url()}{path}"
    else:
        url = f"{url}{path}"

    if req_body:
        return requests.post(url=url, headers=headers, params=params, json=req_body, **kwargs)
    else:
        return requests.post(url=url, headers=headers, params=params, **kwargs)


def http_delete(path: str, url: str = None, headers: dict = None, params: dict = None, use_token: bool = True, **kwargs):
    headers = _make_http_headers(headers=headers, use_token=use_token)

    if not url:
        url = f"{get_url()}{path}"
    else:
        url = f"{url}{path}"

    return requests.delete(url=url, headers=headers, params=params, **kwargs)
