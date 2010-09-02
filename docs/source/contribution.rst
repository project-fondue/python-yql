==========================
Contributing to Python YQL
==========================

If you would like to help out on this project the best place to start is to install the python-yql library and kick the proverbial tyres. Bug-fixes/Features/Patches always welcome. If you have fixed a bug or created a new feature please add branches to the launchpad project.

Source-code
===========

Branches are available at `launchpad <https://launchpad.net/python-yql>`_

You can branch the code with `bzr <http://bzr-vcs.org>`_ 

.. sourcecode:: sh

    bzr branch lp:python-yql

Contributing Code
=================

If you have a fix for a bug or have developed a new feature consider pushing the branch to launchpad and proposing a merge. 

To do this you can follow the following workflow:

.. sourcecode:: sh

    mkdir branches
    bzr branch lp:python-yql branches/<BRANCH_NAME> 
    cd branches/<BRANCH_NAME>
    # Hack on your feature (remember to create tests) :)
    bzr push lp:~<LP_USER>/python-yql/<BRANCH_NAME>

In launchpad visit the url for the branch you've pushed and click "Propose for Merging". Describe what your branch does and what features it adds or what bug it fixes.

Note that branches with tests to cover their changes are far more likely to get accepted and merged.


Filing Bugs
===========

Bugs can be filed over on `bugs.launchpad.net <https://bugs.launchpad.net/python-yql/>`_

When filing a bug be sure to carry out the following:

* Describe the problem and include any tracebacks or error messages.
* Provide the query you are using.
* Feature/Patch Contributors should add their name to the authors file.

