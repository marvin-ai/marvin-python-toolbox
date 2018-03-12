#!/usr/bin/env python
# coding=utf-8

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

import os
import pip
from distutils.version import LooseVersion
import sys
import subprocess
import click
import re
import os.path
import errno
import shutil
from .._compatibility import urlparse
import multiprocessing

__all__ = ['copy']


@click.group('pkg')
def cli():
    pass


@cli.command('pkg-showversion', help='Show the package version.')
@click.pass_context
def version(ctx):
    print(get_version(ctx.obj['package_path']))


@cli.command('pkg-showchanges', help='Show the package changelog.')
@click.pass_context
def log(ctx):
    os.system('less {}'.format(os.path.join(ctx.obj['base_path'], 'CHANGES.md')))


@cli.command('pkg-showinfo', help='Show information about the package.')
@click.pass_context
def info(ctx):
    version = get_version(ctx.obj['package_path'])
    repo = get_git_repository_url(ctx.obj['base_path'])
    branch = get_git_branch(ctx.obj['base_path'])
    commit = get_git_commit(ctx.obj['base_path'])
    tag = get_git_tag(ctx.obj['base_path'])
    tag_commit = get_git_commit(ctx.obj['base_path'], tag=tag)
    # tags = utils.get_git_tags(ctx.obj['base_path'])
    tagged = 'yes' if (tag[1:] == version) else 'no'
    clean = is_git_clean(ctx.obj['base_path'])
    status = 'clean' if clean else 'dirty'
    updated = ('' if (commit == tag_commit and clean) else
               '(dev)' if (not tag[1:] == version) else
               '(should be bumped)')
    pip = 'git+ssh://{repo}@{tag}#egg={pkg}'.format(
        repo=repo[:-4].replace(':', '/'), tag=tag,
        pkg=ctx.obj['package_name'])

    print('')
    print('package: {name}'.format(name=ctx.obj['package_name']))
    print('type:    {type_}'.format(type_=(ctx.obj['type'] or 'unknown')))
    print('version: {version} {updated}'.format(version=version,
                                                updated=updated))
    print('')
    print('branch:  {branch}'.format(branch=branch))
    print('status:  {status}'.format(status=status))
    print('commit:  {commit}'.format(commit=commit))
    print('repo:    {repo}'.format(repo=repo))
    print('')
    print('tagged:  {tagged}'.format(tagged=tagged))
    print('current: {tag} ({tag_commit})'.format(tag=tag,
                                                 tag_commit=tag_commit))
    print('pip url: {pip}'.format(pip=pip))
    print('')


@cli.command('pkg-updatedeps', help='Show information about the package.')
@click.pass_context
def deps(ctx):
    repos = get_repos_from_requirements(ctx.obj['base_path'])
    required_versions = get_tag_from_repo_url(repos)
    latest_versions = get_latest_tags_from_repos(repos)
    installed_pkgs = pip.get_installed_distributions()
    click.echo('')
    for repo in repos:
        status = 'outdated'
        required = required_versions[repo]
        latest = latest_versions[repo]
        try:
            repo_small = repo.split('@')[1]
            pkg_name = repo.split('egg=')[1]
        except IndexError:
            continue
        pkg_name_normalized = pkg_name.lower().replace('_', '-')
        installed = 'unknown'
        installed_list = [
            pkg.version
            for pkg in installed_pkgs
            if pkg.key in [pkg_name_normalized, pkg_name_normalized + '-lib']
        ]
        if installed_list:
            installed = 'v{}'.format(installed_list[0])

        if latest is None or installed is None:
            continue

        if LooseVersion(installed) > LooseVersion(latest):
            status = 'develop'
        elif LooseVersion(installed) < LooseVersion(required):
            status = 'up-to-date (old version installed)'
        elif required == latest:
            status = 'up-to-date'
        msg = '{pkg_name}: {status} (required: {required}, installed: {installed}, latest: {latest})'.format(
            repo=repo_small, pkg_name=pkg_name_normalized, status=status, required=required, installed=installed, latest=latest)
        if status == 'up-to-date' or (status == 'develop' and installed == required):
            color = 'green'
        elif status in ('develop', 'up-to-date (old version installed)') or installed == latest:
            color = 'yellow'
        else:
            color = 'red'
        click.echo(click.style(msg, fg=color))


@cli.command('pkg-bumpversion', help='Bump the package version.')
@click.argument('part', default='patch')
@click.option('--allow-dirty', is_flag=True,
              help='Allow dirty')
@click.option('--force', '-f', is_flag=True,
              help='Alias for --allow-dirty')
@click.option('--yes', '-y', is_flag=True,
              help='Answer yes to all prompts')
@click.pass_context
def bumpversion(ctx, part, allow_dirty, force, yes):
    args = [part]
    allow_dirty = allow_dirty or force

    is_clean = is_git_clean(ctx.obj['base_path'])
    if not is_clean and not allow_dirty:
        print('')
        print('ERROR: Git working directory is not clean.')
        print('')
        print('You can use --allow-dirty or --force if you know what '
              'you\'re doing.')
        exitcode = 1
    else:
        if allow_dirty:
            args.append('--allow-dirty')
        command = ['bumpversion'] + args

        old_version = get_version(ctx.obj['package_path'])
        exitcode = subprocess.call(command, cwd=ctx.obj['base_path'])
        new_version = get_version(ctx.obj['package_path'])

        if exitcode == 0:
            print('Bump version from {old} to {new}'.format(
                old=old_version, new=new_version))
        if yes or click.confirm('Do you want to edit CHANGES.md?'):
            click.edit(filename=os.path.join(ctx.obj['base_path'], 'CHANGES.md'))
    sys.exit(exitcode)


@cli.command('pkg-createtag', help='Create git tag using the package version.')
@click.pass_context
def tag(ctx):
    tag = 'v{}'.format(get_version(ctx.obj['package_path']))
    print('Creating git tag {}'.format(tag))
    command = ['git', 'tag', '-m', '"version {}"'.format(tag), tag]
    sys.exit(subprocess.call(command))


@cli.command('pkg-updatedeps', help='Update requirements.txt.')
@click.option('--install', '-i', is_flag=True)
@click.option('--install-all', '-a', is_flag=True)
@click.pass_context
def update(ctx, install, install_all):
    base_path = ctx.obj['base_path']
    repos = get_repos_from_requirements(base_path)
    required_versions = get_tag_from_repo_url(repos)
    latest_versions = get_latest_tags_from_repos(repos)
    installed_pkgs = pip.get_installed_distributions()
    install_list = ['-e .']
    click.echo('')
    for repo in repos:
        latest = latest_versions[repo]
        required = required_versions[repo]
        try:
            pkg_name = repo.split('egg=')[1]
        except IndexError:
            continue
        pkg_name_normalized = pkg_name.lower().replace('_', '-')
        installed = 'unknown'
        installed_list = [
            pkg.version
            for pkg in installed_pkgs
            if pkg.key in [pkg_name_normalized, pkg_name_normalized + '-lib']
        ]
        if installed_list:
            installed = 'v{}'.format(installed_list[0])

        if LooseVersion(required) < LooseVersion(latest):
            click.echo('Updating {} from {} to {}...'.format(pkg_name, required, latest))
            new_repo = update_repo_tag(repo, latest, path=base_path)
            if LooseVersion(installed) < LooseVersion(latest):
                install_list.append(new_repo)
        elif LooseVersion(installed) < LooseVersion(required):
            install_list.append(repo)
    if install_all:
        install = True
        install_list = ['-r requirements.txt']
    if install:
        for new_repo in install_list:
            new_repo = new_repo.strip()
            click.echo('')
            click.echo('Running `pip install -U {}` ...'.format(new_repo))
            command = ['pip', 'install', '-U'] + new_repo.split(' ')
            exitcode = subprocess.call(command, cwd=base_path)
            if exitcode == 0:
                click.echo('Done.')
            else:
                click.echo('Failed.')
                sys.exit(exitcode)


def copy(src, dest, ignore=('.git', '.pyc', '__pycache__')):
    try:
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*ignore))
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


def get_version(path):
    """Return the project version from VERSION file."""

    with open(os.path.join(path, 'VERSION'), 'rb') as f:
        version = f.read().decode('ascii').strip()
    return version.strip()


def get_repos_from_requirements(path):
    if path is None:
        path = os.path.curdir
    with open(os.path.join(path, 'requirements.txt'), 'r') as fp:
        repos = [line.strip() for line in fp if 'git@' in line and not line.strip().startswith('#')]
    return repos


def get_tag_from_repo_url(repos):
    tags = {}
    for repo in repos:
        if '@' in repo:
            repo_parsed = urlparse(repo)
            repo_path = repo_parsed.path
            tags[repo] = repo_path.split('@')[1]
        else:
            tags[repo] = None
    return tags


def _clone(repo):
    return repo, git_clone(repo, checkout=False, depth=1)


def get_latest_tags_from_repos(repos):
    tags = {}
    if not repos:
        return tags

    pool = multiprocessing.Pool(len(repos))

    repos_ = pool.map(_clone, repos)
    for repo, path in repos_:
        if path:
            tag = get_git_tag(path)
        else:
            tag = None
        tags[repo] = tag
    return tags


def update_repo_tag(repo, tag, path=None):
    if path is None:
        path = os.path.curdir
    ret = ''
    content = ''
    with open(os.path.join(path, 'requirements.txt'), 'r') as fp:
        for line in fp:
            if repo in line:
                line = re.sub(r'@v[0-9]+\.[0-9]+\.[0-9]+', '@{}'.format(tag), line)
                ret += line
            content += line

    with open(os.path.join(path, 'requirements.txt'), 'w') as fp:
        fp.write(content)

    return ret


repo_re = re.compile(r':(\w+)\/(.*)\.git')


def git_clone(repo, dest=None, checkout=True, depth=None, branch=None, single_branch=False):
    if '#egg' in repo:
        repo_parsed = urlparse(repo)
        repo_path = repo_parsed.path
        if '@' in repo_path:
            repo_path = repo_path.split('@')[0]
        repo_path = repo_path.strip('/')
        repo_team, repo_name = tuple(repo_path.split('/'))
        repo = repo_parsed.netloc + ':' + repo_path
    else:
        repo_info = re.search(repo_re, repo)
        if not repo_info:
            return None
        repo_team = repo_info.group(1)
        repo_name = repo_info.group(2)
    if dest is None:
        path = os.path.join(os.path.expanduser('~'), '.marvin-python-toolbox', 'repos')
        dest = os.path.join(path, repo_team, repo_name)

    opts = ''
    if not checkout:
        opts += ' -n'
    if depth:
        opts += ' --depth ' + str(depth)
    if branch:
        opts += ' --branch ' + branch
    if single_branch:
        opts += ' --single-branch'

    if not os.path.exists(dest):
        os.makedirs(dest)
        command = 'git clone {opts} {repo} {dest}'.format(
            opts=opts, repo=repo, dest=dest)
        print(command)
        subprocess.Popen(command.split(), stdout=subprocess.PIPE).wait()

    opts = ''
    if depth:
        opts += ' --depth ' + str(depth)
    print('Fetching latest version from {} repository'.format(repo_name))
    try:
        subprocess.Popen(('git fetch --tags ' + opts).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dest).wait()
    except OSError:
        print('Could not fetch tags from {}'.format(repo_name))
        dest = None

    return dest


def get_git_branch(path=None):
    if path is None:
        path = os.path.curdir
    command = 'git rev-parse --abbrev-ref HEAD'.split()
    branch = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return branch.strip().decode('utf-8')


def get_git_tag(path=None):
    if path is None:
        path = os.path.curdir
    command = 'git rev-list --tags --max-count=1'.split()
    commit = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read().decode('utf-8')
    command = 'git describe --tags {}'.format(commit).split()
    tag = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read().decode('utf-8')
    return tag.strip()


def get_git_commit(path=None, tag=None):
    if path is None:
        path = os.path.curdir
    if tag:
        command = 'git rev-list -n 1 {tag}'.format(tag=tag).split()
    else:
        command = 'git rev-parse HEAD'.split()
    commit = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return commit.strip().decode('utf-8')


def get_git_repository_url(path=None):
    if path is None:
        path = os.path.curdir
    command = 'git config --get remote.origin.url'.split()
    url = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return url.strip().decode('utf-8')


def get_git_tags(path=None):
    if path is None:
        path = os.path.curdir
    command = 'git tag'.split()
    tags = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return sorted(tags.strip().split('\n'), reverse=True)


def is_git_clean(path=None):
    if path is None:
        path = os.path.curdir
    command = 'git diff --quiet HEAD'.split()
    exit_code = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return exit_code
