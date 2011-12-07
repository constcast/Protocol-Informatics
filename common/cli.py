# vim: set sts=4 sw=4 cindent nowrap expandtab:

import cmd, sys

class CommandLineInterface(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "inf> "

    def do_EOF(self, string):
        print string
        sys.exit(0)

    def do_quit(self, string):
        sys.exit(0)

    def do_exit(self, string):
        sys.exit(0)

    def do_help(self, string):
        print string
