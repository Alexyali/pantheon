#!/usr/bin/env python

import os
from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'udt_cc', 'udt4')
    src_dir = path.join(cc_repo, 'src')
    app_dir = path.join(cc_repo, 'app')
    send_src = path.join(app_dir, 'appclient')
    recv_src = path.join(app_dir, 'appserver')

    if args.option == 'setup':
        check_call(['make'], cwd=cc_repo)
        return

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(src_dir)
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(src_dir)
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
