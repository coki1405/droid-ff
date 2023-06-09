from adb_android import adb_android
import fuzzerConfig
import subprocess
import os
import thread
import time
from os.path import isfile, join
from os import listdir

def find_files():
	onlyfiles = [f for f in listdir(fuzzerConfig.path_to_unique_crashes) if isfile(join(fuzzerConfig.path_to_unique_crashes, f))]
	for x in range(len(onlyfiles)):
		print "File being debugged: " + fuzzerConfig.path_to_unique_crashes+onlyfiles[x]
		adb_android.push(fuzzerConfig.path_to_unique_crashes+onlyfiles[x],"/data/local/tmp/"+onlyfiles[x])


def copy_gdb_server_to_device():
	adb_android.push(fuzzerConfig.path_to_thridparty+"android_gdb/gdbserver","/data/local/tmp/")


def adb_forward():
    os.system("adb forward tcp:5039 tcp:5039")
    


def start():
	copy_gdb_server_to_device()
	adb_forward()
	find_files()
	start_threads()

def start_gdb_server_in_device(file):
	out = adb_android.shell("/data/local/tmp/gdbserver :5039 " + fuzzerConfig.target_android_executable + " /data/local/tmp/"+file)
	print out

def start_gdb_in_pc():
	out = os.system(fuzzerConfig.path_to_thridparty+"android_gdb/gdb")
	print out

def start_threads():
	onlyfiles = [f for f in listdir(fuzzerConfig.path_to_unique_crashes) if isfile(join(fuzzerConfig.path_to_unique_crashes, f))]
	try:
		for x in range(len(onlyfiles)):
			thread.start_new_thread(start_gdb_server_in_device,(onlyfiles[x],))
			time.sleep(2)
			thread.start_new_thread(start_gdb_in_pc,())
	except:
		print "unable to start threads"
	time.sleep(5)

