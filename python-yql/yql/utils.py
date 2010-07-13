""""Utility functions"""

METHOD_MAP = {
    "select": "GET",
    "insert": "POST",
    "update": "PUT",
    "delete": "DELETE",
}


def get_http_method(query):
    """Work out if this should be GET, POST, PUT or DELETE"""
    lower_query = query.strip().lower()

    http_method = None
    for key, value in METHOD_MAP.items():
        if key in lower_query:
            http_method = value
    
    if not http_method:
        raise ValueError, "Invalid query. Valid queries must contain"\
                          "one of '%s'" % ", ".join(METHOD_MAP.keys())

    return http_method

