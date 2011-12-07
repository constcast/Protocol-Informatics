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
        if string == "":
            print "You can get a list of possible commands using the command \"list\". Good Luck!"

    def do_list(self, string):
        print "read\t\t- Reads messages from a file"
        print "configuration\t\t- enters the configuration module"
        print ""
        print ""
        print "restart\t\t- restarts the program"
        print "^D\t\t- quits the program"
        print "quit\t\t- quits the program"
        print "exit\t\t- quits the program"

    def do_restart(self, string):
        pass

    def do_read(self, string):
        print string

    def help_read(self, string):
        print string
        print "Command syntax: read <file> [<bro|pcap|ascii>]"
        print ""
        print "Tries to read messages from a file. You need to specify the filename."
        print "The input module will try to guess the 
            
