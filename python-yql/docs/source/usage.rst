=====
Usage
=====

There are three difference ways to use YQL. The public endpoint can be used to query public tables. Beyond this oauth is used to provide access to the private endpoint. First let's take a look at how to query the public endpoint.

Public API Calls
================

The following example shows a simple query using the public endpoint.

.. sourcecode:: python

    >>> import yql
    >>> y = yql.Public()
    >>> query = 'select * from flickr.photos.search where text=panda limit 3';
    >>> y.execute(query)



Using Placeholders in Queries
=============================

This example uses the optional query placeholders which are strings prefixed with ``@`` which are substitutued by dictionary items whose keys match the placeholder. 

.. note::

    Python YQL validates placeholders to check that the correct number of substitutions are passed into the execute function.

.. sourcecode:: python

    >>> import yql
    >>> y = yql.Public()
    >>> query = 'select * from flickr.photos.search where text=@text limit 3';
    >>> y.execute(query, {"text": "panda"})


Private API Calls
=================

Calls can be made to the private YQL API endpoint and use Oauth for authentication. To use authenticated API calls you will need to have signed up for an API key. When you do so be sure to say that you want to be able to make both public and private API calls.

Oauth supports two and three-legged Oauth. Two-legged is used to sign requests and this route can be taken for YQL queries that doen't require access to private data. Using two-legged auth is recommended for general purpose usage of YQL. Three-legged auth is more involved in that it requires the end-user to authorise access to their data. Three-legged auth is used to access contacts and other aspects of Yahoo's Open Social APIs.


Two-legged Auth
---------------

Here's an example of using Two-legged authentication in Python YQL.


.. sourcecode:: python

    import yql 
    
    y = yql.TwoLegged(API_KEY, SHARED_SECRET)
    y.execute("select * from flickr.photos.search where text='panda' limit 3")


Three-legged Auth
-----------------

Three-legged auth requires the user to authenticate with a browser. The idea of this implementation is to try and make using YQL with Three-legged Oauth as painless as possible.

Here's an example:


.. sourcecode:: python

    import yql
    
    y3 = yql.ThreeLegged(API_KEY, SECRET)
    query = 'select * from social.connections where owner_guid=me'
    
    request_token, auth_url = y3.get_auth_url_and_token()
    
    # -- USER AUTHENTICATES HERE --
    
    access_token = y3.get_access_token(request_token, verifier)
    y3.execute(query, token=access_token) 


In the example above the first call made uses the method ``get_auth_url_and_token``. This returns a tuple containing the request token and an authentication url. It's up to the implentation to then send or prompt the user to visit that authenication url in order to login to Yahoo.
    
If a callback was specified in the ``get_auth_url_and_token`` method then your user will be sent to that url when they login. The url will automatically be sent the "verifier" string to use in the "get_access_token" method.

If no callback was specified or was explcitly marked as 'oob' (the default value) then the user will be shown a verfier code which they will have to provide to your application.

The next call, ``get_access_token`` requires the request token and verifier to be sent in order to provide the token that can be used to make authenicated requests.

Once you have got the ``access_token`` it should be used to execute the query.

The Token can be re-used for subsequent requests but after an hour it will expire and will need to be refreshed.

The ``refresh_token()`` method can be used to request a new token using the expired token.

Using Storage Classes
=====================

``yql.storage`` provides a basic way to store Tokens on the filesystem to make it easier to re-use access_tokens in YQL queries.

Here's an example:

.. sourcecode:: python

    import yql
    from yql.storage import FileTokenStore 

    y3 = yql.ThreeLegged(API_KEY, SECRET)

    token_cache_name = "foo"
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cache'))
    token_store = FileTokenStore(path, secret='gfdlgkfruwopiruowsd')

    query = 'select * from social.connections where owner_guid=me'
    stored_token = token_store.get('foo')

    if not stored_token:
        # Do the dance
        request_token, auth_url = y3.get_token_and_auth_url()
        print "Visit url %s and get a verifier string" % auth_url
        verifier = raw_input("Enter the code: ")
        token = y3.get_access_token(request_token, verifier)
        token_store.set('foo', token)
    else:
        # Check access_token is within 1hour-old and if not refresh it
        # and stash it
        token = y3.check_token(stored_token)
        if token != stored_token:
            token_store.set('foo', token)
    
    print y3.execute(query, token=token) 


This example shows a way to do the initial dance including authentication. The access token provided is then stashed away in a file for re-use on subsequent calls. When re-used the ``check_token()`` method is used to check if the token needs refreshing. If it's over an hour old the token is refreshed and returned.

The Storage classes are designed to be extended as necessary so that the user can implement a different backend for storing tokens for re-use. An example would be to use memcache for storage. To create a new storage class all that's needed is to subclass yql.storage.BaseTokenStorage.

.. note::
    
    It's worth bearing in mind that ``yql.storage.FileTokenStorage`` at this point in time, is not intended for heavy duty production use and it's recommended to create a subclass tailored to your own needs. 
