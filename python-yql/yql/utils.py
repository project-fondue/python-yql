""""Utility functions"""

def get_http_method(query):
    """Work out if this should be GET, POST, PUT or DELETE"""
    lower_query = query.strip().lower()

    if lower_query.startswith('select'):
        http_method = "GET"
    elif lower_query.startswith('insert'):
        http_method = "POST"
    elif lower_query.startswith('update'):
        http_method = "PUT"
    elif lower_query.startswith('delete'):
        http_method = "DELETE"
    else:
        raise ValueError, "Invalid query. Valid queries start with "\
                                  "SELECT, INSERT, UPDATE or DELETE"

    return http_method

