"""
Add Jenkins job

"""
from lxml import etree
import getpass
import requests
import sys
import urllib


TEMPLATE = ('<?xml version="1.0" encoding="utf-8"?><project><actions /><descri'
            'ption>Adds or updates chef cookbooks in chef-repo</description><l'
            'ogRotator class="hudson.tasks.LogRotator"><daysToKeep>-1</daysToK'
            'eep><numToKeep>5</numToKeep><artifactDaysToKeep>-1</artifactDaysT'
            'oKeep><artifactNumToKeep>-1</artifactNumToKeep></logRotator><keep'
            'Dependencies>false</keepDependencies><properties><jenkins.plugins'
            '.hipchat.HipChatNotifier_-HipChatJobProperty plugin="hipchat-plug'
            'in@0.1.0"><room>ROOM-NAME</room><startNotification>false</startNo'
            'tification></jenkins.plugins.hipchat.HipChatNotifier_-HipChatJobP'
            'roperty></properties><scm class="hudson.plugins.git.GitSCM" plugi'
            'n="git@1.4.0"><configVersion>2</configVersion><userRemoteConfigs>'
            '<hudson.plugins.git.UserRemoteConfig><name>cookbook</name><refspe'
            'c></refspec><url>{{COOKBOOK-REPO}}</url></hudson.plugins.git.User'
            'RemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.Br'
            'anchSpec><name>master</name></hudson.plugins.git.BranchSpec></bra'
            'nches><localBranch>master</localBranch><disableSubmodules>false</'
            'disableSubmodules><recursiveSubmodules>false</recursiveSubmodules'
            '><doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleCon'
            'figurations><authorOrCommitter>false</authorOrCommitter><clean>fa'
            'lse</clean><wipeOutWorkspace>true</wipeOutWorkspace><pruneBranch'
            'es>false</pruneBranches><remotePoll>false</remotePoll><ignoreNoti'
            'fyCommit>false</ignoreNotifyCommit><useShallowClone>false</useSha'
            'llowClone><buildChooser class="hudson.plugins.git.util.DefaultBui'
            'ldChooser" /><gitTool>Default</gitTool><submoduleCfg class="list"'
            ' /><relativeTargetDir>cookbook</relativeTargetDir><reference></re'
            'ference><excludedRegions></excludedRegions><excludedUsers></exclu'
            'dedUsers><gitConfigName></gitConfigName><gitConfigEmail></gitConf'
            'igEmail><skipTag>false</skipTag><includedRegions></includedRegion'
            's><scmName></scmName></scm><canRoam>true</canRoam><disabled>false'
            '</disabled><blockBuildWhenDownstreamBuilding>false</blockBuildWhe'
            'nDownstreamBuilding><blockBuildWhenUpstreamBuilding>false</blockB'
            'uildWhenUpstreamBuilding><triggers><com.cloudbees.jenkins.GitHubP'
            'ushTrigger plugin="github@1.7"><spec></spec></com.cloudbees.jenki'
            'ns.GitHubPushTrigger></triggers><concurrentBuild>false</concurren'
            'tBuild><builders><hudson.tasks.Shell><command>remy cookbook {{CHE'
            'F-REPO}}</command></hudson.tasks.Shell></builders><publishers><je'
            'nkins.plugins.hipchat.HipChatNotifier plugin="hipchat-plugin@0.1.'
            '0" /></publishers><buildWrappers /></project>')

class JenkinsJob(object):

    HIPCHAT_PROP = 'jenkins.plugins.hipchat.HipChatNotifier_-HipChatJobProperty'

    JOB_PREFIX = 'chef-repo sync '

    def __init__(self, jenkins_host, cookbook_name, cookbook_url, repo_url,
                 username, hipchat_room):
            self.cookbook_name = cookbook_name
            self.cookbook_url = cookbook_url
            self.hipchat = hipchat_room
            self.jenkins_host = jenkins_host
            self.repo_url = repo_url
            self.username = username

    @property
    def job_name(self):
        return '%s%s' % (self.JOB_PREFIX, self.cookbook_name)

    @property
    def jenkins_url(self):
        print self.job_name
        return 'http://%s/createItem?name=%s' % (self.jenkins_host,
                                                 urllib.quote(self.job_name))

    def get_xml(self):
        value = TEMPLATE.replace('{{COOKBOOK-REPO}}', self.cookbook_url)
        doc = etree.fromstring(value.replace('{{CHEF-REPO}}', self.repo_url))
        if self.hipchat is None:
            props = doc.find('properties')
            hipchat = props.find(self.HIPCHAT_PROP)
            props.remove(hipchat)
            publishers = doc.find('publishers')
            hipchat = publishers.find('jenkins.plugins.hipchat.HipChatNotifier')
            publishers.remove(hipchat)
        else:
            hipchat = doc.find('./properties/%s' % self.HIPCHAT_PROP)
            room = hipchat.find('room')
            room.text = self.hipchat
        return etree.tostring(doc, pretty_print=True)

    def create_job(self):
        password = getpass.getpass('Password for %s: ' % self.username)
        response = requests.post(self.jenkins_url,
                                 headers={'content-type': 'text/xml'},
                                 data=self.get_xml(),
                                 auth=(self.username, password))
        if response.status_code != 200:
            sys.stderr.write('Error adding Jenkins job: %s' % response.content)
