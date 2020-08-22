import os
import re
import subprocess


def add_global_options(opt_dict):
    cmd_str = ['./youtube-dl']
    if 'proxy' in opt_dict:
        cmd_str.append('--proxy')
        cmd_str.append(opt_dict['proxy'])
    if 'output_path' in opt_dict:
        cmd_str.append('-o')
        cmd_str.append(opt_dict['output_path'])
    return cmd_str


def get_available_streams(url, opt_dict=None):
    if opt_dict is None:
        opt_dict = {}
    cmd_str = add_global_options(opt_dict)
    cmd_str.append('-F')
    cmd_str.append(url)
    out = subprocess.Popen(cmd_str,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if 'ERROR' in str(stdout):
        return False, []
    outstr = str(stdout).split('\\n')
    isOK = False
    stream_line_started = False
    formats = []
    for line in outstr:
        if line.startswith('format'):
            isOK = True
            stream_line_started = True
            continue
        if stream_line_started:
            line_sections = line.split(' ')
            if line_sections[0].isnumeric():
                formats.append(strjoin(line_sections))
    return isOK, formats


def download_video(url,frm,opt_dict=None):
    if opt_dict is None:
        opt_dict = {}
    cmd_str = add_global_options(opt_dict)
    cmd_str.append('-f')
    cmd_str.append(frm)
    cmd_str.append(url)
    out = subprocess.Popen(cmd_str,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
    regex = re.compile('\d+(\.\d+)?%')
    for stdout_line in iter(out.stdout.readline, ""):
        prog = re.sub(' +', ' ', stdout_line).split(' ')
        if len(prog) > 1:
            if regex.search(prog[1]):
                if not prog[1] == '100%':
                    yield prog[1], prog[3], prog[5], prog[7][:-2]
                else:
                    yield prog[1], prog[3][:-2], '', '00:00'
    out.stdout.close()
    out.wait()


def get_thumbnail(url,opt_dict=None):
    if opt_dict is None:
        opt_dict = {}
    cmd_str = add_global_options(opt_dict)
    cmd_str.append('--write-thumbnail')
    cmd_str.append('--skip-download')
    cmd_str.append(url)
    out = subprocess.Popen(cmd_str,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
    filepath = None
    for stdout_line in iter(out.stdout.readline, ""):
        prog = re.sub(' +', ' ', stdout_line).split(': ')
        if len(prog) > 2:
            if os.path.isfile(prog[2][:-1]):
                filepath = prog[2][:-1]
    out.stdout.close()
    out.wait()
    return filepath

def get_title(url,opt_dict=None):
    if opt_dict is None:
        opt_dict = {}
    cmd_str = add_global_options(opt_dict)
    cmd_str.append('--get-title')
    cmd_str.append('--skip-download')
    cmd_str.append('-f')
    cmd_str.append('worst')
    cmd_str.append(url)
    out = subprocess.Popen(cmd_str,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
    title = ''
    for stdout_line in iter(out.stdout.readline, ""):
        title = stdout_line
    out.stdout.close()
    out.wait()
    return title

def read_batchfile(filename):
    urls = []
    regex = re.compile('^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$')
    with open(filename,'r') as bfile:
        lines = bfile.readlines()
        for line in lines:
            if regex.match(line):
                urls.append(line[:-1])
    return urls

def download_video_batch(url,opt_dict:dict):
    cmd_str = ['./youtube-dl']
    for key, value in opt_dict.items():
        cmd_str.append(key)
        cmd_str.append(value)
    cmd_str.append(url)
    print(cmd_str)
    out = subprocess.Popen(cmd_str,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
    regex = re.compile('\d+(\.\d+)?%')
    for stdout_line in iter(out.stdout.readline, ""):
        prog = re.sub(' +', ' ', stdout_line).split(' ')
        if len(prog) > 1:
            if regex.search(prog[1]):
                if not prog[1] == '100%':
                    yield prog[1], prog[3], prog[5], prog[7][:-2]
                else:
                    yield prog[1], prog[3][:-2], '', '00:00'
    out.stdout.close()
    out.wait()

def strjoin(list_str):
    lstnew = []
    for lstr in list_str:
        if not ( (lstr == '') or (lstr == ',')):
            lstnew.append(lstr)
    return lstnew