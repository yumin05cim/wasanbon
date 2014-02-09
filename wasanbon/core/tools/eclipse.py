import os, sys, subprocess
import yaml
import wasanbon
from wasanbon import lib
import wasanbon.core
from wasanbon import util
from wasanbon.util import git
from wasanbon.core import rtm

def is_installed_eclipse(verbose=False):
    eclipse_dir = os.path.join(wasanbon.rtm_home(), 'eclipse')
    return  os.path.isdir(eclipse_dir)

def install_eclipse(verbose=False, force=False):
    if not is_installed_eclipse() or force:
        url = wasanbon.setting[wasanbon.platform()]['packages']['eclipse']
        util.download_and_unpack(url, wasanbon.rtm_home(), force=force, verbose=verbose)

def launch_eclipse(workbench = ".", argv=None, nonblock=True, verbose=False):
    eclipse_dir = os.path.join(wasanbon.rtm_home(), 'eclipse')
    if sys.platform == 'darwin':
        eclipse_dir = os.path.join(eclipse_dir, 'Eclipse.app/Contents/MacOS')
    curdir = os.getcwd()
    os.chdir(eclipse_dir)

    if sys.platform == 'win32':
        eclipse_cmd = 'eclipse.exe'
    else:
        eclipse_cmd = './eclipse'

    env = os.environ
    env['RTM_ROOT'] = rtm.get_rtm_root()

    if not os.path.isdir(workbench) or workbench == '.':
        if verbose:
            sys.stdout.write("Starting eclipse in current directory.\n")
        cmd = [eclipse_cmd]
    else:
        if verbose:
            sys.stdout.write("Starting eclipse in current package directory(%s).\n" % workbench)
        cmd = [eclipse_cmd, '-data', workbench]

    if argv != None:
        cmd = cmd + argv

    stdout = None if verbose else subprocess.PIPE
    stderr = None if verbose else subprocess.PIPE
    if sys.platform == 'win32':
        p = subprocess.Popen(cmd, creationflags=512, env=env, stdout=stdout, stderr=stderr)
    else:
        p = subprocess.Popen(cmd, env=env, stdout=stdout, stderr=stderr)

    if not nonblock:
        p.wait()

    os.chdir(curdir)


    

