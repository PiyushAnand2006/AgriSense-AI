"""External API client layer.

Every outbound HTTP call to a third-party service goes through the shared
client in ``http_client.py`` so timeout, retry, logging and error handling
are consistent across integrations.
"""
