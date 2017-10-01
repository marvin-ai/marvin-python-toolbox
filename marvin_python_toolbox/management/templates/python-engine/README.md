# {{project.name}} v0.0.1

## Overview

{{project.description}}


## Requirements

_REPLACE: Add here the list of requirements. For example:_

 - Python 2.7
 - Numpy 1.11.0 or higher


## Installation

_REPLACE: Add here the best way to install this engine


## Development

### Getting started

First, create a new virtualenv

```
mkvirtualenv {{project.package}}_env
```

Now install the development dependencies

```
make marvin
```

You are now ready to code.


### Adding new dependencies

It\`s very important. All development dependencies should be added to `setup.py`.

### Running tests

This project uses *[py.test](http://pytest.org/)* as test runner and *[Tox](https://tox.readthedocs.io)* to manage virtualenvs.

To run all tests use the following command

```
marvin test
```

To run specific test

```
marvin test tests/test_file.py::TestClass::test_method
```


### Writting documentation

The project documentation is written using *[Jupyter](http://jupyter.readthedocs.io/)* notebooks. 
You can start the notebook server from the command line by running the following command

```
marvin notebook
```

Use notebooks to demonstrate how to use the lib features. It can also be useful to show some use cases.


### Bumping version

```
marvin pkg-bumpversion [patch|minor|major]
git add . && git commit -m "Bump version"
```


### Tagging version

```
marvin pkg-createtag
git push origin master --follow-tags
```


### Logging

The default log level is set to _WARNING_. You can change the log level at runtime setting another value to one of the following environment variable: `{{project.package|upper}}_LOG_LEVEL` or `LOG_LEVEL`. The available values are _CRITICAL_, _ERROR_, _WARNING_, _INFO_ and _DEBUG_.

Be careful using `LOG_LEVEL`, it may affect another lib.