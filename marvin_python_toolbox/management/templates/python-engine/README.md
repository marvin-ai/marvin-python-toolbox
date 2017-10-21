# {{project.name}} v0.0.1

## Overview

{{project.description}}


## Requirements

_REPLACE: Add here the list of requirements. For example:_

 - Python 2.7
 - Numpy 1.11.0 or higher


## Installation

Use the Marvin toolbox to provision, deploy and start the remote HTTP server.

First, edit the `marvin.ini` file, setting the options within the
`ssh_deployment` section:

1. `host`: the host IP address or name where the engine should be deployed. You
can enable multi-host deployment using `,` to separate hosts
2. `port`: the SSH connection port
3. `user`: the SSH connection username. Currently, only a single user is
supported. This user should be capable of *passwordless sudo*, although it can
use password for the SSH connection

Next, ensure that the remotes servers are provisioned (all required software
are installed):

    marvin engine-deploy --provision

Next, package your engine:

    marvin engine-deploy --package

This will create a compressed archive containing your engine code under the
`.packages` directory.

Next, deploy your engine to remotes servers:

    marvin engine-deploy

By default, a dependency clean will be executed at each deploy. You can skip it
using:

    marvin engine-deploy --skip-clean

Next, you can start the HTTP server in the remotes servers:

    marvin engine-httpserver-remote start

You can check if the HTTP server is running:

    marvin engine-httpserver-remote status

And stop it:

    marvin engine-httpserver-remote stop

After starting, you can test it by making a HTTP request to any endpoint, like:

    curl -v http://example.com/predictor/health

Under the hood, this engine uses Fabric to define provisioning and deployment
process. Check the `fabfile.py` for more information. You can add new tasks or
edit existing ones to match your provisioning and deployment pipeline.

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
