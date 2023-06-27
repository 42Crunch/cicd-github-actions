
def get_conf_from_file(conf_file: dict) -> dict:
    oauth_config = {}

    if "OAuth_implicit_configuration" in conf_file:
        oauth_config["flow"] = "implicit"
        oauth_config["refreshUrl"] = conf_file.get("OAuth_implicit_configuration", {}).get("refresh_url", "")
        oauth_config["authorizationUrl"] = conf_file.get("OAuth_implicit_configuration", {})\
            .get("authorization_url", "")
    elif "OAuth_resource_owner_password_credentials_configuration" in conf_file:
        oauth_config["flow"] = "password"
        oauth_config["refreshUrl"] = conf_file.get("OAuth_resource_owner_password_credentials_configuration", {}).get("refresh_url", "")
        oauth_config["tokenUrl"] = conf_file.get("OAuth_resource_owner_password_credentials_configuration", {}).get("token_url", "")
    elif "OAuth_client_credentials_configuration" in conf_file:
        oauth_config["flow"] = "client_credentials"
        oauth_config["refreshUrl"] = conf_file.get("OAuth_client_credentials_configuration", {}).get("refresh_url", "")
        oauth_config["tokenUrl"] = conf_file.get("OAuth_client_credentials_configuration", {}).get("token_url", "")
    elif "OAuth_authorization_code_configuration" in conf_file:
        oauth_config["flow"] = "authorization_code"
        oauth_config["refreshUrl"] = conf_file.get("OAuth_authorization_code_configuration", {}).get("refresh_url", "")
        oauth_config["tokenUrl"] = conf_file.get("OAuth_authorization_code_configuration", {}).get("token_url", "")
        oauth_config["authorizationUrl"] = conf_file.get("OAuth_authorization_code_configuration", {})\
            .get("authorization_url", "")

    return {
        "pathParameters": conf_file.get("path_parameters", []),
        "pathParametersExceptions": conf_file.get("path_exclusions", []),
        "ignoredHeaders": conf_file.get("ignoredHeaders", []),
        "apiKeys": conf_file.get("api_keys", []),
        "oauth2": oauth_config
    }


__all__ = ["get_conf_from_file"]
