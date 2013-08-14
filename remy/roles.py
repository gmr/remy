"""Remy Role Updater"""
from sh import git
import os
from os import path
import re
import sh
import sys

GITHASH_RE = re.compile(r'commit (\w+)')


class Roles(object):
    """Update Roles to the most current version"""
    ADD = 'Adding'
    UPDATE = 'Updating'
    ROLES = 'roles'
    REPO_PATH = 'repo'

    def __init__(self, repo):
        if path.exists(self.repo_path):
            os.chdir(self.repo_path)
            git.pull('-f', '-u', 'origin', 'master')
        else:
            git.clone(repo, self.REPO_PATH)
            os.chdir(self.repo_path)

        git.submodule('update', '--init', self.ROLES)
        self._metadata = dict()

    def get_submodule_hash(self, submodule_path):
        os.chdir(submodule_path)
        output = str(git('rev-list', '--max-count=1', '--format=%d', 'HEAD'))
        match = GITHASH_RE.match(output)
        os.chdir(self.repo_path)
        return match.groups()[0]

    @property
    def repo_path(self):
        return path.realpath(path.join(self.workspace_path, self.REPO_PATH))

    def update_roles(self):
        os.chdir('%s/%s' % (self.repo_path, self.ROLES))
        git.pull('-f', '-u', 'origin', 'master')
        os.chdir(self.repo_path)

        message = '%s %s %s %s' % (self.UPDATE, self.ROLES, 'to',
                                   self.get_submodule_hash(self.ROLES))
        git.commit('-m', message, '.gitmodules', self.ROLES)
        sys.stdout.write('Committed %s [%s]\n' % (self.ROLES, message))
        try:
            git.push('origin', 'master')
        except sh.ErrorReturnCode_1:
            pass

    @property
    def workspace_path(self):
        return path.realpath(os.path.abspath(os.environ['WORKSPACE']))
