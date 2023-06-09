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
    for x in range(0, 100):
        sys.stdout.write('... ')
    print "\n"


def move_unique_crash(filename):
    full_file_path = fuzzerConfig.path_for_crash_samples + filename[10:]
    args = ("cp", full_file_path, fuzzerConfig.path_to_unique_crashes)
    subprocess.Popen(args, stdout=subprocess.PIPE)


def find_base_module(filename):
    tombstone = fuzzerConfig.path_for_confirmed_samples + filename

    f = open(tombstone, 'r')
    for line in f:
        if fuzzerConfig.target_android_executable + ':' in line:
            return line


def find_module_symbol_path(my_string):
    start = my_string.find(fuzzerConfig.target_android_executable + ":") + 13
    end = my_string[start:].find(' ') + start
    return my_string[start:end]


def start():
    onlyfiles = [f for f in listdir(fuzzerConfig.path_for_confirmed_samples) if
                 isfile(join(fuzzerConfig.path_for_confirmed_samples, f))]

    for x in range(len(onlyfiles)):
        if onlyfiles[x] == ".DS_Store":
            continue
        else:
            f = open(fuzzerConfig.path_for_confirmed_samples + onlyfiles[x], "r")
            traces = f.readlines()
            pc_address = "00000000"
            for y in range(0, len(traces)):
                if "fault addr" in traces[y]:
                    start = traces[y].index("fault addr") + 11
                    pc_address = traces[y][start:]
                    break

            if pc_address not in new_crashes.keys():
                new_crashes[pc_address] = onlyfiles[x]

    print "listing all crashes" + str(new_crashes.items())
    draw_line()
    for pc_address, filename in new_crashes.iteritems():

        base_module_name = find_base_module(filename)
        print "Module Name : " + 'stagefright'
        symbols_file_of_crash = find_module_symbol_path(base_module_name)
        print "Path to the file with symbols : " + symbols_file_of_crash
        tombstone = fuzzerConfig.path_for_confirmed_samples + filename
        print "Path to the tombstone file :" + tombstone

        args = (fuzzerConfig.ndkstack, "-sym", fuzzerConfig.symbols, "-dump", tombstone)

        execute = subprocess.Popen(args, stdout=subprocess.PIPE)
        strings1 = ("Stack", "frame", "pc", base_module_name)

        for line in execute.stdout.readlines():
            if all(s in line for s in strings1):
                print "Stack Frame pc value : " + line[20:30].strip()
                break
        method = ''
        for i in base_module_name[base_module_name.find('stagefright:') + 13:].split(' ')[1:-1]:
            method += i
        print "Method and Filename Responsible for crash : " + symbols_file_of_crash.split('/')[-1] + ' - ' + method

        draw_line()
        move_unique_crash(filename)
