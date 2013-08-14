"""Remy Cookbook Manager"""
from sh import git
import json
import os
from os import path
import re
import sh
import sys

GITHASH_RE = re.compile(r'commit (\w+)')
COOKBOOK_URL_RE = re.compile(r'cookbook\s+([\w\:\.\/\-\@]+)\s')
METADATA_RE = re.compile(r'^(\s+|)([\w]+)\s+(["\']|)([\w\s,\-\.@\:]+)(["\']|)'
                         r'([\s+\n]|,\s+(["\']|)([\w\s,\.@\:]+)(["\']|)'
                         r'[\s+\n])', re.M)
METADATA_KEYWORDS = ['name', 'maintainer', 'maintainer_email', 'license',
                     'description', 'version', 'recipe']


class CookbookManager(object):
    """The CookbookManager manages a chef-repo's cookbooks using Git submodules
    for each cookbook.

    It is meant to be invoked by the Github Jenkins callback, where it will
    update the chef-repo repository with the cookbook that was updated and
    any included submodules.

    """
    ADD = 'Adding'
    UPDATE = 'Updating'
    COOKBOOK = 'cookbook'
    COOKBOOK_PATH = 'cookbook'
    DEPENDENCY = 'dependency cookbook'
    REPO_PATH = 'repo'

    def __init__(self, repo):
        if path.exists(self.repo_path):
            os.chdir(self.repo_path)
            git.pull('-f', '-u', 'origin', 'master')
        else:
            git.clone(repo, self.REPO_PATH)
            os.chdir(self.repo_path)

        git.submodule('update', '--init')
        self._metadata = dict()

    def add_submodule(self, cookbook_name, submodule_path, cookbook_url):
        os.chdir(self.repo_path)
        sys.stdout.write('Adding cookbook: %s\n' % cookbook_name)
        git.submodule('add', cookbook_url, submodule_path)
        git.submodule('update', '--init')

    def commit_object(self, action, object_type, object_name, path_to_object):
        message = '%s %s %s %s %s' % (action, object_type, object_name,
                                      'at' if action == self.ADD else 'to',
                                      self.get_cookbook_hash(path_to_object))
        git.commit('-m', message, '.gitmodules', path_to_object)
        sys.stdout.write('Committed %s [%s]\n' % (path_to_object, message))

    @property
    def cookbook_dependencies(self):
        dependencies_path = path.join(self.cookbook_path, 'dependencies.json')
        if not path.exists(dependencies_path):
            return {}
        return json.loads(open(dependencies_path).read())

    @property
    def cookbook_name(self):
        return self.cookbook_metadata.get('name').strip()

    @property
    def cookbook_metadata(self):
        if self._metadata:
            return self._metadata
        if not path.exists(self.cookbook_metadata_path):
            return dict()
        output = dict()
        with open(self.cookbook_metadata_path) as handle:
            metadata = handle.read()
            for match in METADATA_RE.finditer(metadata):
                if match.group(2) in METADATA_KEYWORDS:
                    if match.group(2) == 'recipe':
                        output[match.group(2)] = {'name': match.group(4),
                                                  'desc': match.group(8)}
                    else:
                        output[match.group(2)] = match.group(4)
        self._metadata = output
        return self._metadata

    @property
    def cookbook_metadata_path(self):
        return path.realpath(os.path.join(self.cookbook_path, 'metadata.rb'))

    @property
    def cookbook_path(self):
        return path.realpath(path.join(self.workspace_path, self.COOKBOOK_PATH))

    @property
    def cookbook_git_url(self):
        os.chdir(self.cookbook_path)
        match = COOKBOOK_URL_RE.match(str(git.remote('-v')))
        os.chdir(self.repo_path)
        return match.groups()[0]

    @property
    def dependency_cookbooks(self):
        return self.cookbook_dependencies.get('cookbooks', dict())

    def get_cookbook_hash(self, submodule_path):
        os.chdir(submodule_path)
        output = str(git('rev-list', '--max-count=1', '--format=%d', 'HEAD'))
        match = GITHASH_RE.match(output)
        os.chdir(self.repo_path)
        return match.groups()[0]

    def process_cookbook(self):
        if not self.cookbook_name:
            sys.stderr.write('Could not find cookbook name, exiting\n')
            sys.exit(1)

        commits = [self.process_cookbook_submodule(self.cookbook_name,
                                                   self.submodule_path,
                                                   self.cookbook_git_url,
                                                   self.COOKBOOK)]

        for dependency in self.dependency_cookbooks:
            dep_path = 'cookbooks/%s' % dependency
            dep_url = self.dependency_cookbooks[dependency]['url']
            commits.append(self.process_cookbook_submodule(dependency,
                                                           dep_path,
                                                           dep_url,
                                                           self.DEPENDENCY))
        # Push any changes
        if any(commits):
            git.push('origin', 'master')

    def process_cookbook_submodule(self, cookbook_name, submodule_path,
                                   cookbook_url, cookbook_type):
        if cookbook_name is None:
            sys.stdout.write('No work to perform this execution\n')
            return
        if self.repo_has_submodule(submodule_path):
            self.update_submodule(submodule_path)
            action = self.UPDATE
        else:
            self.add_submodule(cookbook_name, submodule_path, cookbook_url)
            action = self.ADD

        try:
            self.commit_object(action, cookbook_type, cookbook_name,
                               submodule_path)
            return True
        except sh.ErrorReturnCode_1:
            return False

    def repo_has_submodule(self, submodule_path):
        return path.exists(submodule_path)

    def update_submodule(self, submodule_path):
        os.chdir(submodule_path)
        git.pull('-f', '-u', 'origin', 'master')
        os.chdir(self.repo_path)

    @property
    def repo_path(self):
        return path.realpath(path.join(self.workspace_path, self.REPO_PATH))

    @property
    def submodule_path(self):
        return 'cookbooks/%s' % self.cookbook_name

    @property
    def workspace_path(self):
        return path.realpath(os.path.abspath(os.environ['WORKSPACE']))
