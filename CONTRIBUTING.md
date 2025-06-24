# Contributing

Contributions are welcome and are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs through GitHub

If you are reporting a bug, please include:

-   Your operating system name and version.
-   Any details about your local setup that might be helpful in
    troubleshooting.
-   Detailed steps to reproduce the bug.

When you post python stack traces please quote them using
[markdown blocks](https://help.github.com/articles/creating-and-highlighting-code-blocks/).

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" is
open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with
"feature" or "starter_task" is open to whoever wants to implement it.

### Documentation

BotLab could always use better documentation,
whether as part of the official BotLab docs,
in docstrings, `docs` or even on the web as blog posts or
articles.

### Submit Feedback

The best way to send feedback is to file an issue on GitHub.

If you are proposing a feature:

-   Explain in detail how it would work.
-   Keep the scope as narrow as possible, to make it easier to
    implement.
-   Remember that this is a volunteer-driven project, and that
    contributions are welcome :)

## Pull Request Guidelines

Before you submit a pull request from your forked repo, check that it
meets these guidelines:

1.  The pull request should include tests, either as doctests,
    unit tests, or both.
2.  If the pull request adds functionality, the docs should be updated
    as part of the same PR. Doc string are often sufficient, make
    sure to follow the sphinx compatible standards.
3.  The pull request should work for Python 3.8+.
4.  Code will be reviewed by re running the unittests, flake8 and syntax
    should be as rigorous as the core Python project.
5.  Please rebase and resolve all conflicts before submitting.
6.  If you are asked to update your pull request with some changes there's
    no need to create a new one. Push your changes to the same branch.

## Documentation

BotLab uses [Doxygen](https://www.doxygen.nl) to generate a static html page in the
`docs/` directory.  Generate using `Doxygen` from the `docs/` directory.

## Testing

All python tests can be run with:

`./pytest`
    
Alternatively, you can run a specific test with:

`./pytest -m test_bot`

## Linting

Lint the project with:

`ruff`

## API documentation

Generate the documentation with:

`cd docs && Doxygen`

## Translations

We use [gettext](https://docs.python.org/3/library/gettext.html) to translate BotLab. The
key is to instrument the strings that need translation using
`_ = gettext.gettext`. Once this is imported in
the `localization.py` module, all you have to do is to `_("Wrap your strings")` using the
underscore `_` "function".
