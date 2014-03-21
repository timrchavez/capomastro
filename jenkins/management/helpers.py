from requests.exceptions import HTTPError

REQUIRED_PLUGINS = ["notification"]


def verify_jenkinsserver(server):
    """
    Perform some perfunctory tests to check if a server is suitable for use with
    Capomastro.
    """
    messages = []
    try:
        client = server.get_client()
    except HTTPError as e:
        messages.append("ERROR: %s" % str(e))
    else:
        plugins = client.get_plugins()
        missing_plugins = []
        for plugin in REQUIRED_PLUGINS:
            if not plugin in plugins:
                missing_plugins.append(plugin)
        if missing_plugins:
            messages.append("Missing plugins: " + ",".join(missing_plugins))
    return messages
