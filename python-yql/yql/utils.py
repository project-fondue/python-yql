""""Utility functions"""

METHOD_MAP = (
    ("insert", "POST"),
    ("update", "PUT"),
    ("delete", "DELETE"),
)


def get_http_method(query):
    """Work out if this should be GET, POST, PUT or DELETE"""
    lower_query = query.strip().lower()

    http_method = "GET"
    for method in METHOD_MAP:
        if method[0] in lower_query:
            http_method = method[1]
            break
    
    return http_method

