Remy
====
Remy is a tool for managing Chef repositories and automating the addition and
management of cookbooks with a chef server using Jenkins and GitHub.

For the Jenkins integration to work properly, the following plugins are required:

 - Github Plugin
 - Jenkins Git client plugin

The following Jenkins plugin is optionally supported:

 - Jenkins Hipchat Plugin

Remy requires Python 2.6 or 2.7

[![PyPI version](https://badge.fury.io/py/remy.png)](http://badge.fury.io/py/remy) [![Downloads](https://pypip.in/d/remy/badge.png)](https://crate.io/packages/pamqp) [![Build Status](https://travis-ci.org/gmr/remy.png?branch=master)](https://travis-ci.org/gmr/remy)

Commands
--------
Remy currently supports the following commands

 - cookbooks: This command should be invoked by jenkins to automatically add or update cookbooks or their dependencies as submodules in chef-repo
 - github: Install the Jenkins service hook into a GitHub Project
 - new-cookbook: Setup a new cookbook job in Jenkins
