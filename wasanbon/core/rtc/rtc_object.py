import sys, os, subprocess


import wasanbon

from wasanbon.util import git
from wasanbon.util import github_ref
from wasanbon.core.rtc import rtcprofile
from wasanbon.core.rtc import packageprofile
from wasanbon.core.rtc import build
#from wasanbon.core.rtc import repository
import repository


class RtcObject():

    def __init__(self, path, verbose=False):
        self._path = path
        self._rtc_xml = ""
        self._rtcprofile = None
        if os.path.isdir(os.path.join(path, '.git')):
            self._protocol = 'git'
        else:
            self._protocol = 'hg'

        for root, dirs, files in os.walk(path):
            if 'RTC.xml' in files:
                self._rtc_xml = os.path.join(root, 'RTC.xml')
                return
        raise wasanbon.RTCProfileNotFoundException()
        pass

    @property
    def rtcprofile(self):
        if not self._rtcprofile:
            self._rtcprofile = rtcprofile.RTCProfile(self._rtc_xml)
        return self._rtcprofile

    @property
    def packageprofile(self):
        return packageprofile.PackageProfile(self.rtcprofile)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self.rtcprofile.basicInfo.name
    
    @property
    def language(self):
        return self.rtcprofile.language.kind

    def build(self, verbose=False):
        if self.language == 'C++':
            build.build_rtc_cpp(self.rtcprofile, verbose=verbose)
        elif self.language == 'Python':
            build.build_rtc_python(self.rtcprofile, verbose=verbose)
        elif self.language == 'Java':
            build.build_rtc_java(self.rtcprofile, verbose=verbose)
        pass
    
    @property
    def repository(self):
        git_obj = wasanbon.util.git.GitRepository(self.path)
        return repository.RtcRepository(self.name, url=git_obj.url, desc="", hash=git_obj.hash)

    def clean(self, verbose=False):
        if self.language == 'C++':
            build.clean_rtc_cpp(self.rtcprofile, verbose=verbose)
        pass

    def is_git_repo(self, verbose=False):
        try:
            git_obj = wasanbon.util.git.GitRepository(self.path, init=True, verbose=verbose)        
        except wasanbon.RepositoryNotFoundException, ex:
            return False
        return True

    def git_init(self, verbose=False):
        git_obj = wasanbon.util.git.GitRepository(self.path, init=True, verbose=verbose)
        git_obj.add(['.'], verbose=verbose)
        git_obj.add(['.project', '.gitignore'], verbose=verbose)
        first_comment = 'This if first commit. This repository is generated by wasanbon'    
        git_obj.commit(first_comment, verbose=verbose)
        return self.git

    def github_init(self, user, passwd, verbose=False):
        github_obj = github_ref.GithubReference(user, passwd)
        repo = github_obj.create_repo(self.name)
        git.git_command(['remote', 'add', 'origin', 'git@github.com:' + user + '/' + self.name + '.git'], verbose=verbose, path=self.path)
        git.git_command(['push', '-u', 'origin', 'master'], verbose=verbose, path=self.path)    
        return self

    def github_pullrequest(self, user, passwd, title, body, verbose=False):
        github_obj = github_ref.GithubReference(user, passwd)
        github_obj.pullrequest(self.repository.url, title, body, verbose=verbose)
        return self

    def git_branch(self, verbose=False):
        #git symbolic-ref --short HEAD
        p = git.git_command(['symbolic-ref', '--short', 'HEAD'], verbose=False, path=self.path, pipe=True)
        p.wait()
        return p.stdout.readline().strip()

    @property
    def git(self):
        return git.GitRepository(self.path)

    @property
    def hg(self):
        return None

    def commit(self, comment, verbose=False):
        self.git.commit(comment, verbose=verbose)
        return self

    def checkout(self, verbose=False, hash=''):
        self.git.checkout(verbose=verbose, hash=hash)
        return self

    def pull(self, verbose=False):
        self.git.pull(verbose=verbose)
        return self

    def push(self, verbose=False):
        self.git.push(verbose=verbose)
        return self

    def execute_standalone(self, argv = [], verbose=False):
        exe_file = self.packageprofile.getRTCExecutableFilePath()

        env = os.environ.copy()
        if not 'HOME' in env.keys():
            env['HOME'] = wasanbon.get_home_path()
            if verbose:
                sys.stdout.write(' - Environmental Variable  HOME (%s) is added.\n' % gitenv['HOME'])


        if self.language == 'C++':
            cmd = [exe_file]
        elif self.language == 'Python':
            cmd = ['python', exe_file]

        if verbose:
            sys.stdout.write(' - Executing ... %s\n' % cmd)

        cmd = cmd + argv
        
        stdout = None if verbose else subprocess.PIPE
        stderr = None if verbose else subprocess.PIPE

        p = subprocess.call(cmd, env=env, stdout=stdout, stderr=stderr)

        return p
