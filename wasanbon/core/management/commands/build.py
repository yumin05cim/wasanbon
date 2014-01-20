#!/usr/bin/env python
import os, sys
import wasanbon
from wasanbon.core import package as pack
class Command(object):
    def __init__(self):
        pass

    def alternative(self):
        _package = pack.Package(os.getcwd())
        return [rtc.name for rtc in _package.rtcs]

    def execute_with_argv(self, argv, verbose, force, clean):
        wasanbon.arg_check(argv, 3)
        _package = pack.Package(os.getcwd())

        build_all = True if 'all' in argv else False
        found_flag = False
        if sys.platform == 'win32':
            verbose=True
            pass

        for rtc in _package.rtcs:
            if build_all or rtc.name in argv:
                sys.stdout.write(' @ Building RTC %s\n' % rtc.name)
                rtc.build(verbose=verbose)
                found_flag = True
                pass
            pass

        if not found_flag:
            sys.stdout.write(' - Can not find RTC.\n')


                    

