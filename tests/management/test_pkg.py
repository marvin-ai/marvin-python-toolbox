#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from click.testing import CliRunner

try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.management.pkg import _clone
from marvin_python_toolbox.management.pkg import copy
from marvin_python_toolbox.management.pkg import get_git_branch
from marvin_python_toolbox.management.pkg import is_git_clean
from marvin_python_toolbox.management.pkg import get_git_tags
from marvin_python_toolbox.management.pkg import get_git_repository_url
from marvin_python_toolbox.management.pkg import get_git_tag
from marvin_python_toolbox.management.pkg import get_git_commit
from marvin_python_toolbox.management.pkg import get_tag_from_repo_url
from marvin_python_toolbox.management.pkg import get_repos_from_requirements


@mock.patch('marvin_python_toolbox.management.pkg.open')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.join')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
def test_get_repos_from_requirements(curdir_mocked, join_mocked, open_mocked):
    join_mocked.return_value = '/tmp'

    get_repos_from_requirements(path=None)

    join_mocked.assert_called_with(curdir_mocked, 'requirements.txt')
    open_mocked.assert_called_with('/tmp', 'r')

    get_repos_from_requirements(path='/path')

    join_mocked.assert_called_with('/path', 'requirements.txt')
    open_mocked.assert_called_with('/tmp', 'r')


def test_get_tag_from_repo_url():
    repos = ['http://www.xxx.org:80/tag@/repo.html']

    tags = get_tag_from_repo_url(repos)

    assert tags == {'http://www.xxx.org:80/tag@/repo.html': '/repo.html'}

    repos = ['http://www.xxx.org:80/tag/repo.html']

    tags = get_tag_from_repo_url(repos)

    assert tags == {'http://www.xxx.org:80/tag/repo.html': None}


@mock.patch('marvin_python_toolbox.management.pkg.git_clone')
def test_clone(git_mocked):
    git_mocked.return_value = 1
    repo = 'http://xxx.git'
    result = _clone(repo)

    assert result == (repo, 1)
    git_mocked.assert_called_once_with(repo, checkout=False, depth=1)


@mock.patch('marvin_python_toolbox.management.pkg.shutil.ignore_patterns')
@mock.patch('marvin_python_toolbox.management.pkg.shutil.copytree')
def test_copy(copytree_mocked, ignore_mocked):
    src = '/xpto'
    dest = '/xpto_dest'
    ignore = ('.git')
    ignore_mocked.return_value = 1
    copy(src, dest, ignore)

    copytree_mocked.assert_called_once_with(src, dest, ignore=1)
    ignore_mocked.assert_called_once_with(*ignore)


@mock.patch('marvin_python_toolbox.management.pkg.subprocess.PIPE')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
@mock.patch('marvin_python_toolbox.management.pkg.subprocess.Popen')
def test_get_git_branch(popen_mocked, curdir_mocked, pipe_mocked):
    mockx = mock.MagicMock()
    mockx.stdout.read.return_value = 'branch '
    popen_mocked.return_value = mockx

    branch = get_git_branch()

    popen_mocked.assert_called_once_with(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=pipe_mocked, cwd=curdir_mocked)

    assert branch == 'branch'

    branch = get_git_branch(path='/tmp')

    popen_mocked.assert_called_with(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=pipe_mocked, cwd='/tmp')


@mock.patch('marvin_python_toolbox.management.pkg.subprocess.PIPE')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
@mock.patch('marvin_python_toolbox.management.pkg.subprocess.Popen')
def test_get_git_tag(popen_mocked, curdir_mocked, pipe_mocked):
    mockx = mock.MagicMock()
    mockx.stdout.read.return_value = 'tag '
    popen_mocked.return_value = mockx

    tags = get_git_tag()

    popen_mocked.assert_called_with(['git', 'describe', '--tags', 'tag'], stdout=pipe_mocked, cwd=curdir_mocked)

    assert tags == 'tag'

    tags = get_git_tag(path='/tmp')

    popen_mocked.assert_called_with(['git', 'describe', '--tags', 'tag'], stdout=pipe_mocked, cwd='/tmp')


@mock.patch('marvin_python_toolbox.management.pkg.subprocess.PIPE')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
@mock.patch('marvin_python_toolbox.management.pkg.subprocess.Popen')
def test_get_git_commit(popen_mocked, curdir_mocked, pipe_mocked):
    mockx = mock.MagicMock()
    mockx.stdout.read.return_value = 'commit '
    popen_mocked.return_value = mockx

    commit = get_git_commit()

    popen_mocked.assert_called_once_with(['git', 'rev-parse', 'HEAD'], stdout=pipe_mocked, cwd=curdir_mocked)

    assert commit == 'commit'

    commit = get_git_commit(path='/tmp')
    popen_mocked.assert_called_with(['git', 'rev-parse', 'HEAD'], stdout=pipe_mocked, cwd='/tmp')

    commit = get_git_commit(tag='tag')
    popen_mocked.assert_called_with(['git', 'rev-list', '-n', '1', 'tag'], stdout=pipe_mocked, cwd=curdir_mocked)


@mock.patch('marvin_python_toolbox.management.pkg.subprocess.PIPE')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
@mock.patch('marvin_python_toolbox.management.pkg.subprocess.Popen')
def test_get_git_repository_url(popen_mocked, curdir_mocked, pipe_mocked):
    mockx = mock.MagicMock()
    mockx.stdout.read.return_value = 'url '
    popen_mocked.return_value = mockx

    url = get_git_repository_url()

    popen_mocked.assert_called_once_with(['git', 'config', '--get', 'remote.origin.url'], stdout=pipe_mocked, cwd=curdir_mocked)

    assert url == 'url'

    url = get_git_repository_url(path='www.xxx.com')

    popen_mocked.assert_called_with(['git', 'config', '--get', 'remote.origin.url'], stdout=pipe_mocked, cwd='www.xxx.com')


@mock.patch('marvin_python_toolbox.management.pkg.subprocess.PIPE')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
@mock.patch('marvin_python_toolbox.management.pkg.subprocess.Popen')
def test_get_git_tags(popen_mocked, curdir_mocked, pipe_mocked):
    mockx = mock.MagicMock()
    mockx.stdout.read.return_value = 'git\ntags '
    popen_mocked.return_value = mockx

    tags = get_git_tags()

    popen_mocked.assert_called_once_with(['git', 'tag'], stdout=pipe_mocked, cwd=curdir_mocked)

    assert tags == ['tags', 'git']

    tags = get_git_tags(path='/tmp')

    popen_mocked.assert_called_with(['git', 'tag'], stdout=pipe_mocked, cwd='/tmp')


@mock.patch('marvin_python_toolbox.management.pkg.subprocess.PIPE')
@mock.patch('marvin_python_toolbox.management.pkg.subprocess.Popen')
@mock.patch('marvin_python_toolbox.management.pkg.os.path.curdir')
def test_is_git_clean(curdir_mocked, popen_mocked, pipe_mocked):
    mockx = mock.MagicMock()
    mockx.stdout.read.return_value = 'done'
    popen_mocked.return_value = mockx

    clean = is_git_clean()
    popen_mocked.assert_called_once_with(['git', 'diff', '--quiet', 'HEAD'], stdout=pipe_mocked, cwd=curdir_mocked)

    assert clean == 'done'

    clean = is_git_clean('/tmp')

    popen_mocked.assert_called_with(['git', 'diff', '--quiet', 'HEAD'], stdout=pipe_mocked, cwd='/tmp')

    assert clean == 'done'
