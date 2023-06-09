import time
from os.path import isfile, join
from os import listdir
import re
import subprocess
import sys
import fuzzerConfig

new_crashes = {}
regex_address = re.compile("pc\s\S*")

def draw_line():
    print "\n"
    for x in range(0,100):
        sys.stdout.write('... ')
    print "\n"


def move_unique_crash(filename):
	full_file_path = fuzzerConfig.path_for_crash_samples+filename[10:]
        args = ("cp", full_file_path,fuzzerConfig.path_to_unique_crashes)
        execute = subprocess.Popen(args, stdout=subprocess.PIPE)

def find_base_module(filename):
    tombstone = fuzzerConfig.path_for_confirmed_samples + filename

    #args = (fuzzerConfig.ndkstack, "-sym", fuzzerConfig.symbols, "-dump", tombstone)

    #execute = subprocess.Popen(args, stdout=subprocess.PIPE)

    # Build base_of_module
    strings = ("pid", "tid", "stagefright")

    f = open(tombstone, 'r')

    for line in f: #execute.stdout.readlines():
        #if all(s in line for s in strings):
        if 'stagefright:' in line:
            #my_string = line[(line.index("name:") + 5):line.index(">>>")]
            #return my_string.strip()
            return line

def find_module_symbol_path(my_string):
            #args = ("find",fuzzerConfig.symbols,"-name",my_string.strip())
            #args = ("find", "stagefright", "-name", my_string.strip())
            #execute = subprocess.Popen(args, stdout=subprocess.PIPE)
            start = my_string.find('stagefright:') + 13

            end = my_string[start:].find(' ') + start
            return my_string[start:end]
            #for line in execute.stdout.readlines():
            #    return line.strip()

def start():
    onlyfiles = [f for f in listdir(fuzzerConfig.path_for_confirmed_samples) if isfile(join(fuzzerConfig.path_for_confirmed_samples, f))]

    for x in range(len(onlyfiles)):
        if(onlyfiles[x]==".DS_Store"):
            pass
        else:
            f = open(fuzzerConfig.path_for_confirmed_samples+onlyfiles[x], "r")
            traces = f.readlines()
            pc_check = 0
            for y in range(0, len(traces)):
                if "fault addr" in traces[y]:
                    start = traces[y].index("fault addr")+11
                    pc_address = traces[y][start:]
                    pc_check = 1
                    break
                '''if ("fault addr" in traces[y]):
                    pc_address = regex_address.findall(traces[y + 1])
                    pc_address = (str)(pc_address[0])
                    pc_address = pc_address[3:]
                    pc_check = 1
                    break'''
            if (pc_check == 0):
                pc_address = "00000000"


            # save the file as a new crash(or not) and log the findings
            if (pc_address not in new_crashes.keys()):
                new_crashes[pc_address] = onlyfiles[x]


    print "listing all crashes" + str(new_crashes.items())
    draw_line()
    for pc_address, filename in new_crashes.iteritems():

        base_module_name = find_base_module(filename)
        print "Module Name : " +'stagefright'
        symbols_file_of_crash = find_module_symbol_path(base_module_name)
        print "Path to the file with symbols : "+symbols_file_of_crash
        tombstone =fuzzerConfig.path_for_confirmed_samples+filename
        print "Path to the tombstone file :"+tombstone

        args = ( fuzzerConfig.ndkstack, "-sym", fuzzerConfig.symbols, "-dump", tombstone)

        execute = subprocess.Popen( args, stdout=subprocess.PIPE)
        strings1 = ("Stack", "frame", "pc",base_module_name)

        for line in execute.stdout.readlines():
            if all(s in line for s in strings1):
                print "Stack Frame pc value : "+line[20:30].strip()
                break
        args1 = [ fuzzerConfig.addr2line, "-C","-f", "-e", symbols_file_of_crash,line[20:30].strip()]
        method = ''
        for i in base_module_name[base_module_name.find('stagefright:') + 13:].split(' ')[1:-1]:
            method += i
        print "Method and Filename Responsible for crash : " + symbols_file_of_crash.split('/')[-1] + ' - ' + method

        #execute1 = subprocess.Popen(args1, stdout=subprocess.PIPE)
        #for line in execute1.stdout.readlines():
        #    print line[:-1]
        draw_line()
	move_unique_crash(filename)
