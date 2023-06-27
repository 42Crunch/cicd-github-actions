def parse_conf_file(conf_file: dict) -> None:

    # check if conf file is valid
    host = conf_file.get("host")
    if not host:
        raise Exception("host not found")

    base_path = conf_file.get("base_path")
    if not base_path:
        raise Exception("base_path not found")

    # check protocols
    protocols = conf_file.get("protocols", {})
    https = protocols.get("https", False)
    http = protocols.get("http", False)

    if not https and not http:
        raise Exception("at least one protocol must be True")

    # check if security is well-defined

    oauth2 = False
    api_key = False

    # review mandatory fields in OAuth2
    if "OAuth_implicit_configuration" in conf_file:
        oauth2 = True
        if not conf_file["OAuth_implicit_configuration"].get("authorization_url", None):
            raise Exception("authorization_url not found in OAuth_implicit_configuration")

    elif "OAuth_resource_owner_password_credentials_configuration" in conf_file:
        oauth2 = True
        if not conf_file["OAuth_resource_owner_password_credentials_configuration"].get("token_url", None):
            raise Exception("token_url not found in OAuth_resource_owner_password_credentials_configuration")

    elif "OAuth_client_credentials_configuration" in conf_file:
        oauth2 = True
        if not conf_file["OAuth_client_credentials_configuration"].get("token_url", None):
            raise Exception("token_url not found in OAuth_client_credentials_configuration")

    elif "OAuth_authorization_code_configuration" in conf_file:
        oauth2 = True
        if not conf_file["OAuth_authorization_code_configuration"].get("authorization_url", None):
            raise Exception("authorization_url not found in OAuth_authorization_code_configuration")
        if not conf_file["OAuth_authorization_code_configuration"].get("token_url", None):
            raise Exception("token_url not found in OAuth_authorization_code_configuration")

    api_keys = conf_file.get("api_keys", [])
    if api_keys:
        api_key = True

    if oauth2 and api_key:
        raise Exception("Only one security protocol can be used")


__all__ = ["parse_conf_file"]
