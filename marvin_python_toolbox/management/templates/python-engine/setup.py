
# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

from os.path import dirname, join
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def _get_version():
    """Return the project version from VERSION file."""

    with open(join(dirname(__file__), '{{project.package}}/VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
    return version


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
    author='Marvin AI Researcher',
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
        'six>=1.10.0',
        'scikit-learn==0.18.2',
        'scipy==0.19.1',
        'numpy==1.13.1',
        'pandas==0.20.3',
        'matplotlib==2.0.2',
        'git+https://github.com/marvin-ai/marvin-python-toolbox@master#egg=marvin_python_toolbox',
        'git+https://github.com/marvin-ai//marvin-python-common-lib@master#egg=marvin_python_common'
    ],
    tests_require=[
        'pytest>=2.6.4',
        'pytest-cov>=1.8.1',
        'mock>=2.0.0',
        'virtualenv>=15.0.1',
        'tox>=2.2.0',
    ],
    cmdclass={
        'test': Tox,
    },
)
