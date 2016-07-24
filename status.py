import requests
import re

class Status:

    # constructor: read a js code file in MTR website,
    # form list of tuples for stations lines and stations
    def __init__(self):
        url = "http://www.mtr.com.hk/share/customer/js/jplannerdata_en.js"
        f = requests.get(url)

        self.lines = re.findall(
            'caption[0-9]*\s*=\s*"--(.*?)--";\s*style[0-9][\s\S]*?lineValue[0-9]*\s*=\s"(.*?)";',
            f.text, re.IGNORECASE | re.MULTILINE)

        self.stations = re.findall(
            'caption[0-9]*\s*=\s*"(.*?)";\s*lineValue[0-9]*\s*=\s"(.*?)";',
            f.text, re.IGNORECASE | re.MULTILINE)

        self.status_good = ['good service', 'resume']
        self.status_fail = ['delay', 'fail', 'faulty', 'disrupt', 'accident']


    # pass in single message about MTR status
    # output a tuple for [0] the status (True = good / False = fail)
    # and [1] the set of MTR lines that the message described
    def line(self, message):

        found_line = []
        message = message.strip().lower()
        
        # loop through lines to see if line is mentioned
        for l in self.lines:
            if(l[0].strip().lower() in message):
                found_line.extend(l[1].strip().lower().split(','))
                
        # loop through station names if station is mentioned
        for s in self.stations:
            if(s[0].strip().lower() in message):
                found_line.extend(s[1].strip().lower().split(','))

        # special: check if light rail, it is not in MTR's script
        if('light rail' in message or 'lightrail' in message):
            found_line.append('lightrail')

        # special: check if disney, in script it is called disneyland resort
        # and is part of tung chung line, so may not match all the time
        if('disney' in message):
            found_line.append('disney')
            
        found_line = set(found_line)

        # determine if status is good or fail, return right away.
        # here we assume good status is overriding because there
        # could be messages like "the faulty xxx is resumed..."
        for g in self.status_good:
            if(g.strip().lower() in message):
                return (True, found_line)

        for f in self.status_fail:
            if(f.strip().lower() in message):
                return (False, found_line)

        return (None, found_line)


    # pass in a series of messages about MTR status
    # in ascending chronological order
    # output a tuple for [0] the status (True = good / False = fail)
    # and [1] the set of MTR lines that the STATUS described
    def overall(self, messages):

        lines_mentioned = set();
        lines_failed = set();
        
        for message in messages:
            status_line = self.line(message)
            
            if(status_line[0] == False):
                # if fail, add lines to fail set
                lines_failed = lines_failed.union(status_line[1])
                lines_mentioned = lines_mentioned.union(status_line[1])
                
            if(status_line[0] == True):
                # if good, remove lines from fail set 
                lines_failed = lines_failed.difference(status_line[1])
                lines_mentioned = lines_mentioned.union(status_line[1])
                
        if(len(lines_failed) == 0):
            return (True, lines_mentioned)
        else:
            return (False, lines_failed)


# when this file executed individually, run test
if(__name__ == "__main__"):
    
    status = Status()

    message1 = "1800 The lighting system at Mong Kok is resumed. Backup floodlights have been mobilised for contingency"
    message2 = "1800 The lighting system at island line, central is resumed. Backup floodlights have been mobilised for contingency"
    message3 = "message about sunny bay station"
    message4 = "tseung kwan o line disruption"

    print(status.line(message1))
    print(status.line(message2))
    print(status.line(message3))
    print(status.line(message4))
