"""
Manage GitHub Hooks

"""
import getpass
import json
import requests
import sys

GITHUB_HOST = 'github.com'


class GitHubHook(object):
    """Installs a Jenkins callback hook in GitHub"""
    def __init__(self, github_host, repo_owner, repo_name, hook_url):
        self._github_host = github_host
        self._repo_owner = repo_owner
        self._repo_name = repo_name
        self._hook_url = hook_url
        pass

    @property
    def _github_url(self):
        return 'https://%s/api/v3' % self._github_host or GITHUB_HOST

    def _post_jenkins_hook(self, username, password):
        payload = {"name": "jenkins",
                   "active": True,
                   "events": ["push"],
                   "config": {"jenkins_hook_url": self._hook_url}}
        url = '%s/repos/%s/%s/hooks' % (self._github_url,
                                        self._repo_owner,
                                        self._repo_name)
        response = requests.post(url,
                                 auth=(username, password),
                                 headers={'Content-type': 'application/json'},
                                 data=json.dumps(payload))
        if response.status_code == 200:
            sys.stdout.write('Callback hook enabled\n')
            return True
        sys.stderr.write('Error from Github (%s): %s\n' %
                         (response.status_code, response.json()['message']))
        return False

    def add_callback_hook(self, username=None):
        if username is None:
            username = self._repo_owner
        password = getpass.getpass('Password for %s: ' % username)
        self._post_jenkins_hook(username, password)
