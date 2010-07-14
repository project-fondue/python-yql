""""Utility functions"""

METHOD_MAP = (
    ("insert", "POST"),
    ("update", "PUT"),
    ("delete", "DELETE"),
    ("show", "GET"),
    ("desc", "GET"),
    ("select", "GET"),
)


def get_http_method(query):
    """Work out if this should be GET, POST, PUT or DELETE"""
    lower_query = query.strip().lower()

    http_method = None
    for method in METHOD_MAP:
        if method[0] in lower_query:
            http_method = method[1]
            break
    
    if not http_method:
        raise ValueError, "Invalid query. Valid queries must contain"\
                          "one of '%s'" % ", ".join(dict(METHOD_MAP).keys())

    return http_method

