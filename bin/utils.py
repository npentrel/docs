import re
import yaml
import sys
import os
import subprocess
import json 
import hashlib

def md5_file(file, block_size=2**20):
    md5 = hashlib.md5()

    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(128*md5.block_size), b''):
            md5.update(chunk)

    return md5.hexdigest()

def log_command_output(cmd, path, logfile, wait=False):
    with open(logfile, 'a') as f:
        p = subprocess.Popen(cmd, cwd=path, stdout=f, stderr=f)
        if wait is True:
            p.wait()

def shell_value(args, path=None):
    if path is None:
        path = os.getcwd()

    if isinstance(args , str):
        r = re.compile("\s+")
        args = r.split(args)

    p = subprocess.Popen(args, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()

    return str(r[0].decode().rstrip())

def get_commit(path=None):
    if path is None:
        path = os.getcwd()

    return shell_value('git rev-parse --verify HEAD', path)

def get_branch(path=None):
    if path is None:
        path = os.getcwd()

    return shell_value('git symbolic-ref HEAD', path).split('/')[2]

def expand_tree(path, input_extension='yaml'):
    file_list = []
    for root, subFolders, files in os.walk(path):
        for file in files:
            f = os.path.join(root, file)

            try:
                if f.rsplit('.', 1)[1] == input_extension:
                    file_list.append(f)
            except IndexError:
                continue

    return file_list

def ingest_yaml(filename):
    o = []
    with open(filename, 'r') as f:
        data = yaml.load_all(f)

        for i in data:
            o.append(i)

    if len(o) == 1:
        o = o[0]

    return o
def ingest_yaml_list(filename):
    o = ingest_yaml(filename)

    if isinstance(o, list):
        return o
    else:
        return [o]

def ingest_json(filename):
    o = []
    with open(filename, 'r') as f:
        for doc in f.readlines():
            o.append(json.loads(doc))

    if len(o) == 1:
        o = o[0]

    return o

def get_conf_file(file):
    return file.rsplit('.', 1)[0] + '.yaml'

def build_platform_notification(title, content):
    if sys.platform.startswith('darwin'):
        return 'growlnotify -n "mongodb-doc-build" -a "Terminal.app" -m %s -t %s' % (title, content)
    if sys.platform.startswith('linux'):
        return 'notify-send "%s" "%s"' % (title, content)
