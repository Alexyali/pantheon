import sys
from os import path
import json
import signal
import subprocess
import project_root
from helpers.helpers import check_output, timeout_handler, TimeoutError


def read_port_from_proc(proc):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)

    try:
        port_info = proc.stdout.readline().split(':')
    except TimeoutError:
        sys.exit('Cannot get port within 10 seconds\n')
    else:
        signal.alarm(0)

        if port_info[0] == 'Listening on port':
            return port_info[1].strip()
        else:
            return None


def who_runs_first(cc):
    cc_src = path.join(project_root.DIR, 'src', cc + '.py')

    cmd = ['python', cc_src, 'run_first']
    run_first = check_output(cmd).strip()

    if run_first == 'receiver':
        run_second = 'sender'
    elif run_first == 'sender':
        run_second = 'receiver'
    else:
        sys.exit('Must specify "receiver" or "sender" runs first')

    return run_first, run_second


def parse_remote_path(remote_path, cc=None):
    ret = {}

    ret['host_addr'], ret['pantheon_dir'] = remote_path.split(':')
    ret['ip'] = ret['host_addr'].split('@')[-1]
    ret['ssh_cmd'] = ['ssh', ret['host_addr']]

    ret['src_dir'] = path.join(ret['pantheon_dir'], 'src')
    if cc is not None:
        ret['cc_src'] = path.join(ret['src_dir'], cc + '.py')

    ret['test_dir'] = path.join(ret['pantheon_dir'], 'test')
    ret['tunnel_manager'] = path.join(ret['test_dir'], 'tunnel_manager.py')

    return ret


def query_clock_offset(ntp_addr, ssh_cmd=None):
    worst_clock_offset = None

    ntp_cmd = [['ntpdate', '-quv', ntp_addr]]
    if ssh_cmd is not None:
        cmd = ssh_cmd + ntp_cmd[0]
        ntp_cmd.append(cmd)

    for cmd in ntp_cmd:
        max_run = 5
        curr_run = 0

        while True:
            curr_run += 1
            if curr_run > max_run:
                sys.stderr.write('Failed after 5 attempts\n')
                break

            try:
                offset = check_output(cmd).rsplit(' ', 2)[-2]
                offset = abs(float(offset)) * 1000
            except subprocess.CalledProcessError:
                sys.stderr.write('Failed to get clock offset\n')
            except ValueError:
                sys.stderr.write('Cannot convert clock offset to float\n')
            else:
                if worst_clock_offset is None or offset > worst_clock_offset:
                    worst_clock_offset = offset
                break

    return worst_clock_offset


def get_git_summary(args_dict):
    sh_cmd = (
        'echo -n \'git branch: \'; git rev-parse --abbrev-ref @ | head -c -1; '
        'echo -n \' @ \'; git rev-parse @; git submodule foreach --quiet '
        '\'echo $path @ `git rev-parse HEAD`; '
        'git status -s --untracked-files=no --porcelain\'')
    local_git_summary = check_output(sh_cmd, shell=True, cwd=project_root.DIR)

    if args_dict['mode'] == 'remote':
        r = parse_remote_path(args_dict['remote_path'])
        cmd = r['ssh_cmd'] + ['cd %s; %s' % (r['pantheon_dir'], sh_cmd)]
        remote_git_summary = check_output(cmd)

        if local_git_summary != remote_git_summary:
            sys.exit('Repository differed between local and remote sides')

    return local_git_summary


def save_test_metadata(args_dict):
    meta = {}
    meta = args_dict.copy()

    meta.pop('all')
    meta.pop('schemes')
    meta.pop('save_metadata')
    meta['git_summary'] = get_git_summary(args_dict)

    metadata_path = path.join(
        project_root.DIR, 'test', 'pantheon_metadata.json')

    with open(metadata_path, 'w') as metadata:
        json.dump(meta, metadata, sort_keys=True, indent=4,
                  separators=(',', ': '))