'''
Created on Jul 8, 2012

@author: daubsi
'''
    
import re

def analyze():
    filename_client = "/Users/daubsi/Dropbox/ftp_big_client"
    filename_server = "/Users/daubsi/Dropbox/ftp_big_server"
    
    number_regex = "(([1-9])|([1-9]\d)|(1\d\d)|(2([0-4]\d|5[0-5])))" # matches 1-255    
    
    in_file_client = open(filename_client, "r") 
    in_file_server = open(filename_server, "r")
    
    commands_in = [
               "USER\s\w+",
               "PASS\s[\w<>]+",
               "ACCT\s\w+",
               "CWD\s.+",
               "CDUP",  # 0x43,0x44,0x55,0x50
               "SMNT\s.+",
               "QUIT",
               "REIN",
               "PORT\s({0},){1}{0}".format(number_regex,"{5}"),
               "PASV",
               "TYPE\sA",
               "TYPE\sE",
               "TYPE\sI",
               "TYPE\sL\s{0}".format(number_regex),
               "TYPE\sA\sN",
               "TYPE\sA\sT",
               "TYPE\sA\sC",
               "TYPE\sE\sN",
               "TYPE\sE\sT",
               "TYPE\sE\sC",
               "STRU\sF",
               "STRU\sR",
               "STRU\sP",
               "MODE\sS",
               "MODE\sB",
               "MODE\sC",
               "RETR\s.+",
               "STOR\s.+",
               "STOU",
               "APPE\s.+",                    
               "ALLO\s[1-9]\d+",
               "ALLO\sR\s[1-9]\d+",
               "REST\s[\x20-\x7e]+",
               "RNFR\s.+",
               "RNTO\s.+",
               "ABOR",
               "DELE\s.+",
               "RMD\s.+",
               "MKD\s.+",
               "PWD",
               "LIST",
               "LIST\s.+",
               "NLST",
               "NLST\s.+",
               "SITE\s.+",
               "SYST",
               "STAT",
               "STAT\s.+",
               "HELP",
               "HELP\s.+",
               "NOOP"
               ]
    
    return_codes_in = [
               "110",
               "120",
               "125",
               "150",
               "200",
               "202",
               "211",
               "212",
               "213",
               "214",
               "215",
               "220",
               "221",
               "225",
               "226",
               "227",
               "230",
               "250",
               "257",
               "331",
               "332",
               "350",
               "421",
               "425",
               "426",
               "450",
               "451",
               "452",
               "500",
               "501",
               "502",
               "503",
               "504",
               "530",
               "532",
               "550",
               "551",
               "552",
               "553"]
    
    commands = set()                
    for elem in commands_in:
        commands.add("{0}{1}{2}".format("^",elem,"\x0d\x0a$"))
    
    matches = dict()
    for elem in commands:
        matches[elem] = False
    
    return_codes = set()
    for elem in return_codes_in:
        return_codes.add("{0}{1}{2}".format("^",elem,"\s.+\x0d\x0a$"))  
        return_codes.add("{0}{1}{2}{3}{4}".format("^",elem,"\-\s(.+|(\x0d\x0a))+",elem,"\s.+\x0d\x0a$"))
        
    return_codes_matches = dict()
    for elem in return_codes:
        return_codes_matches[elem]=False
    
    regexstring = '\*+ (\w+) ([0-9]+) ([0-9]+) ([0-9]+) (.*)'
    for line in in_file_client:        
        m = re.match(regexstring, line)
        if m: 
            # connectionID = m.group(1)
            # messageNumber = int(m.group(2))
            # flowMessageNumber = int(m.group(3))
            # contentLength = int(m.group(4))
            content = m.group(5)                            
            ascii_payload = convert_payload(content)
    
            # found = False
            commands_copy = set()
            for elem in commands:
                commands_copy.add(elem) 
            for elem in commands_copy:
                m = re.match(elem, ascii_payload)
                if m:
                    #print "Found: " + elem
                    matches[elem] = True
                    commands.remove(elem)
                    # found = True
                    break
            #if not found:
            #    print elem, " not found in testdata"
            #    commands.remove(elem)
            if len(commands)==0:
                break;                            
        else:
            print "Line did not match regex ", line
    in_file_client.close()
    
    for line in in_file_server:        
        m = re.match(regexstring, line)
        if m: 
            # connectionID = m.group(1)
            # messageNumber = int(m.group(2))
            # flowMessageNumber = int(m.group(3))
            # contentLength = int(m.group(4))
            content = m.group(5)                            
            ascii_payload = convert_payload(content)
        
            # found = False
            return_codes_copy = set()
            for elem in return_codes:
                return_codes_copy.add(elem) 
            for elem in return_codes_copy:
                m = re.match(elem, ascii_payload)
                if m:
                    #print "Found: " + elem
                    return_codes_matches[elem] = True
                    return_codes.remove(elem)
                    # found = True
                    break
            #if not found:
            #    print elem, " not found in testdata"
            #    commands.remove(elem)
            if len(return_codes)==0:
                break;                            
        else:
            print "Line did not match regex ", line
    in_file_server.close()
    # print results
    for elem in matches:    
        _str = elem[0:-3]
        _str = _str[1:]
        if matches[elem]==False:
            print _str," : ", matches[elem]

    for elem in return_codes_matches:
        _str = elem[0:-3]
        _str = _str[1:]
        if return_codes_matches[elem]==False:
            print _str," : ", return_codes_matches[elem]

    
    
def convert_payload(content):
    idx = 0
    payload = ""
    while idx < len(content):
        data = content[idx] + content[idx + 1]
        payload += chr(int(data,16))            
        idx += 2
    return payload
    
    
if __name__ == '__main__':
    analyze()
    
