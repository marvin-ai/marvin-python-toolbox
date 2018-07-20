from __future__ import print_function

import os
import shutil
from os.path import dirname, join
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install


REQUIREMENTS_TESTS = [
    'pytest>=2.6.4',
    'pytest-cov>=1.8.1',
    'mock>=2.0.0',
    'virtualenv>=15.0.1',
    'tox>=2.2.0',
]

def _get_version():
    """Return the project version from VERSION file."""

    with open(join(dirname(__file__), '{{project.package}}/VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
    return version


def _hooks(dir):
    _set_autocomplete()
    _install_notebook_extension()


def _set_autocomplete():
    import marvin_python_toolbox as toolbox
    virtualenv = os.environ.get('VIRTUAL_ENV', None)

    if virtualenv:
        postactivate = os.path.join(virtualenv, 'bin', 'postactivate')

        if os.path.exists(postactivate):
            shutil.copy(
                os.path.join(toolbox.__path__[0], 'extras', 'marvin_bash_completion'),
                os.path.join(virtualenv, 'marvin_bash_completion')
            )

            command = 'source "{}"'.format(os.path.join(virtualenv, 'marvin_bash_completion'))

            with open(postactivate, 'r+') as fp:
                lines = fp.readlines()
                fp.seek(0)
                configured = False
                for line in lines:
                    if 'marvin_bash_completion' in line:
                        # Replacing old autocomplete configuration
                        fp.write(command)
                        configured = True
                    else:
                        fp.write(line)

                if not configured:
                    fp.write(command)
                    # 'Autocomplete was successfully configured'
                fp.write('\n')
                fp.truncate()


def _install_notebook_extension():
    import marvin_python_toolbox as toolbox

    install_command = [
        "jupyter",
        "nbextension",
        "install",
        os.path.join(toolbox.__path__[0], 'extras', 'notebook_extensions', 'main.js'),
        "--destination",
        "marvin.js",
        "--sys-prefix",
        "--overwrite"
    ]

    os.system(' '.join(install_command))

    enable_command = [
        "jupyter",
        "nbextension",
        "enable",
        "marvin",
        "--sys-prefix"
    ]

    os.system(' '.join(enable_command))


class develop(_develop):
    def run(self):
        _develop.run(self)
        self.execute(_hooks, (self.install_lib,), msg="Running develop preparation task")


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_hooks, (self.install_lib,), msg="Running install preparation task")


class Tox(TestCommand):
    """Run the test cases using TOX command."""

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        import sys
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        else:
            # Run all tests by default
            args = ['-c', join(dirname(__file__), 'tox.ini'), 'tests']
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name='{{project.package}}',
    version=_get_version(),
    url='{{project.url}}',
    description='{{project.description}}',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='{{mantainer.name}}',
    maintainer='{{mantainer.name}}',
    maintainer_email='{{mantainer.email}}',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'scikit-learn==0.18.2',
        'scipy==0.19.1',
        'numpy==1.13.1',
        'pandas==0.20.3',
        'matplotlib==2.0.2',
        'marvin-python-toolbox==0.0.4',
        'Fabric==1.14.0',
    ],
    tests_require=REQUIREMENTS_TESTS,
    extras_require={
        'testing': REQUIREMENTS_TESTS,
    },
    cmdclass={
        'test': Tox, 'develop': develop, 'install': install
    },
)
