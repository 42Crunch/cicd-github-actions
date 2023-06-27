from xliic_cli.helpers import http_post, set_url, set_token


class API_PATHS:
    LOGIN = "/api/release/1.0/authentication/login/"


def login_with_terminal(user: str, password: str, service_url: str):
    req_body = {
        "username": user,
        "password": password,
    }

    try:
        response = http_post(path=API_PATHS.LOGIN, url=service_url, req_body=req_body, use_token=False)

        if response.status_code == 200:
            response_body = response.json()
            token = response_body.get("token")
            set_token(token)
            set_url(service_url)

            return

        else:
            raise Exception(f"Error logging in {response.reason}")

    except Exception as e:
        raise Exception(f"Error logging in {e}")


def login_with_browser(service_url: str) -> None:
    raise NotImplementedError()


__all__ = ("login_with_terminal", "login_with_browser")
