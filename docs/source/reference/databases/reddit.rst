Reddit
==========

The connection to Reddit is based on the `praw <https://praw.readthedocs.io/>`_ library.

Dependency
----------

* praw


Parameters
----------

Required:

* ``subreddit`` is the name of the subreddit from which the data is fetched.
* ``clientId`` is the unique identifier issued to the client when creating credentials on Reddit. Refer to the [First Steps](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps) guide for more details on how to get this and the next two parameters.
* ``clientSecret`` is the secret key obtained when credentials are created that is used for authentication and authorization.
* ``userAgent`` is a string of your choosing that explains your use of the the Reddit API. More details are available in the guide linked above.

Optional:


Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE reddit_data WITH ENGINE = 'reddit', PARAMETERS = {
        "subreddit": "AskReddit",
        "client_id": "abcd",
        "clientSecret": "abcd1234",
        "userAgent": "Eva DB Staging Build"
   };

Supported Tables
----------------

* ``submissions``: Lists top submissions in the given subreddit. Check `databases/reddit/table_column_info.py` for all the available columns in the table.

.. code-block:: sql

   SELECT * FROM hackernews_data.search_results LIMIT 3;

.. note::

   Looking for another table from Hackernews? Please raise a `Feature Request <https://github.com/georgia-tech-db/evadb/issues/new/choose>`_.
