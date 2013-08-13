"""
CLI stub for arg parsing and command invocation

"""
import argparse
import os
import socket
import sys

from remy import cookbooks
from remy import github
from remy import __description__
from remy import __version__


def add_cookbook_mgmt_options(parser):
    """Add the cookbook management command and arguments.

    :rtype: argparse.ArgumentParser

    """
    cookbook = parser.add_parser('cookbook', help='Invoke in a Jenkins job to '
                                                  'Update a cookbook in '
                                                  'chef-repo')
    cookbook.add_argument('repo', action='store',
                          help='Git URL for chef-repo')
    cookbook.set_defaults(func='process_cookbook')

def add_github_hook_options(parser):
    """Add the github jenkins hook command and arguments.

    :rtype: argparse.ArgumentParser

    """
    cookbook = parser.add_parser('github', help='Install the Jenkins callback '
                                                'hook in a GitHub repository')
    cookbook.add_argument('owner', action='store',
                          help='The owner of the GitHub repo')
    cookbook.add_argument('repo', action='store',
                          help='The GitHub repository name')
    domain = socket.gethostname()
    example = 'jenkins.%s' % domain
    cookbook.add_argument('jenkins_hook_url', action='store',
                          help='The jenkins hook URL. For example %s' % example)

    cookbook.add_argument('-g', '--github-host',
                          action='store',
                          dest='github',
                          default=github.GITHUB_HOST,
                          help='Override github.com for a '
                               'GitHub::Enterprise host')
    cookbook.add_argument('-u', '--username',
                          action='store',
                          dest='username',
                          help='Specify a different username than the repo '
                               'owner')

    cookbook.set_defaults(func='github_hooks')




def argparser():
    """Build the argument parser

    :rtype: argparse.ArgumentParser

    """
    parser = argparse.ArgumentParser(description=__description__)
    sparser = parser.add_subparsers()
    add_cookbook_mgmt_options(sparser)
    add_github_hook_options(sparser)
    return parser


def main():
    args = argparser().parse_args()
    if args.func == 'process_cookbook':
        if not os.environ.get('WORKSPACE'):
            sys.stderr.write('This command should be run from a Jenkins job\n')
            sys.exit(1)
        obj = cookbooks.CookbookManager(args.repo)
        obj.process_cookbook()

    elif args.func == 'github_hooks':
        obj = github.GitHubHook(args.github, args.owner, args.repo,
                                args.jenkins_hook_url)
        obj.add_callback_hook(args.username)



if __name__ == '__main__':
    main()