# vim: set sts=4 sw=4 cindent nowrap expandtab:

import cmd, sys, os

class CommandLineInterface(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "inf> "
        sys.path.append("../")

        import common
        self.configuration = common.config.Configuration()

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
        else:
            cmd.Cmd.do_help(self, string)

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
        print "Trying to restart"
        executable = sys.executable
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.execvp(executable, args)

    def do_configuration(self, string):
        import common

        try:
            newConfig = common.config.Configuration(string)
        except Exception as inst:
            print "Error: Could not read configuration file \"%s\": %s" % (string, inst)
            print "Using old config ..."
            return
        self.configuration = newConfig


        
    def help_configuration(self):
        print "Command syntax: configuration <file>"
        print ""
        print "Reads a configuration from <file>. Configuration format"
        print "is yaml. It needs to be in the same format as the configuration"
        print "files presented to the command line switch -c"

        
        

    def do_read(self, string):
        import common
        words = string.split()
        if len(words) == 1:
            # we only received an input file. try to guess the format
            print "Error. Format guessing not yet implemented ..."
            return
            print "Trying to read file \"" + words[0] + "\"..."
            print "No format specified. Trying to guess format. Please specify format"
            sequences = None
            for reader in common.input.__all__[1:-1]:
                print "Trying reader " + reader + "..."
                    
        elif len(words) == 2:
            try:
                # we expect a file and a format string
                if words[1] == "pcap":
                    sequences = common.input.Pcap(words[0], 0, True)
                elif words[1] == "bro":
                    sequences = common.input.Bro(words[0], 0, True)
                elif words[2] == "ascii":
                    sequences = common.input.ASCII(words[0], 0, True)
                else:
                    print "Error: Format \"" + words[1] + "\" unknown to reader"
            except Exception as inst:
                print ("FATAL: Error reading input file '%s':\n %s" % (file, inst))
        else:
            # unknown command format
            print "Error in read syntax."
            self.help_read()
        

    def help_read(self):
        print "Command syntax: read <file> [<bro|pcap|ascii>]"
        print ""
        print "Tries to read messages from a file. You need to specify the filename."
        print "The input module will try to guess the input format. If you specify a"
        print "format, of either bro, pcap, or ascii, the appropriate reader will be"
        print "called."
            
