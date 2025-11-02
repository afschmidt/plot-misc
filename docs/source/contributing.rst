
===========================
Contributing to the project
===========================

We welcome contributions from all users to the project:

1. Documentation fixes/updates
2. Example notebooks to illustrate features/methods
3. Bug fixes
4. New code

However, we ask that contributors please follow these guidelines when contributing to the package. This allows us to retain some level of homogeneity throughout a project and will make it easily to maintain and improve in the long run.

A list of current contributors can be found in the project root. 

1. Please ensure that all code follows the Python `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html>`_ standard.
2. Please ensure that your code is well commented, so that programmers of varying abilities have a good chance in following it.
3. Please make sure that any code, or bug-fixes you contribute are accompanied by a `pytest <https://docs.pytest.org>`_.
4. Please run a full `pytest <https://docs.pytest.org>`_ prior to merging your code and ensure all tests pass (or that your new code has not caused any new test failures).
5. Please make sure that all modules, classes, functions (even private ones) have docstrings. This enables us to easily produce high quality documentation and improves the user experience. 
   This module uses Numpy docstrings for the most part. Please follow `this <https://developer.lsst.io/python/numpydoc.html>`_ excellent guide if unsure.
6. Any HOWTOs or extended user documentation should be written in `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ (preferably) or `Markdown <https://en.wikipedia.org/wiki/Markdown>`_.
7. We incorporate Jupyter notebooks into the documentation, so please ensure they are fairly quick to run and do not have reams of output associated with them. Also, please make sure that all output is collapsed (removed) prior to committing the notebook to git.
8. Please make sure that any test data you submit is small and compressed and please do not commit any individual level data that is not already in the public domain.


Commit Message Format
=====================

All commits must follow the **Conventional Commits** format. This is enforced 
by a Git hook that validates your commit message before the commit is created.

Format
------

Commit messages must follow this structure::

    type(scope): description

Where:

- **type**: required (see valid types below)
- **scope**: optional, no spaces allowed (use hyphens)
- **description**: required, minimum 10 characters

Valid Types
-----------

========== ============================================
Type       When to Use
========== ============================================
feat       New plotting function or feature
fix        Bug fix
docs       Documentation (docstrings, README, guides)
style      Code style/formatting (no functional changes)
refactor   Code restructuring (no functional changes)
test       Adding or updating tests
chore      Maintenance (dependencies, configs, build)
perf       Performance improvements
data       Example datasets or demo updates
========== ============================================

Requirements
------------

1. **Type must be valid**: One of the types listed above
2. **Scope rules**: Optional, but no spaces (use hyphens for multi-word scopes)
3. **Description**: Minimum 10 characters, be descriptive and specific
4. **Line length**: First line should be under 72 characters (warning only)

Examples
--------

Good examples::

    feat(forest): add confidence interval display
    fix(heatmap): correct color scaling for negative values
    docs(readme): add installation instructions
    test(volcano): add edge case validation
    refactor(utils): simplify color palette generation
    chore(deps): update matplotlib to 3.8.0

Bad examples::

    fix: bug                    # Too short (only 3 chars)
    feat(forest plot): add CI   # Space in scope
    update: change docs         # Invalid type

Common Scopes
-------------

For consistency, use these scopes where applicable:

- ``forest``, ``volcano``, ``heatmap``, ``survival``, ``barchart``
- ``utils``, ``core``, ``api``
- ``deps``, ``ci``, ``hooks``

Why These Rules?
----------------

- **Clear history**: Understand changes at a glance
- **Automatic changelogs**: Tools can generate release notes
- **Better collaboration**: Team members understand changes quickly
- **Easy searching**: Find commits by type

The 10-character minimum forces meaningful descriptions. Compare:

- Not helpful: ``fix: bug``
- Helpful: ``fix(heatmap): correct color scaling for negative values``

Bypassing the Hook
------------------

For emergencies only::

    git commit --no-verify -m "Emergency fix"

**Warning**: Only use this for genuine emergencies.

Contact
=======

If you want to contribute and are unsure on any of these points please `contact <amand.schmidt@ucl.ac.uk>`_ the lead developer. 

Many thanks in advance!



