import numpy as np
import subprocess
import os
import time
import sys
import re


start = time.time()
print("python:")
path = "/udata/delia/presets/"


files = []
direcs = []

# make a list of all bank folders and sort it alphabetically
files_in_dst_dir = []
patches_in_source_dir = []


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


bank_folders = get_immediate_subdirectories(path)
bank_folders.sort(key=str.lower)
current_banks = int(bank_folders[-1][0:3])

# check if there are enough free bank slots
if (current_banks > 126):
    print("yikes, too many banks")
    sys.exit(-1)

# enough free, so make a new bank
subprocess.run("mkdir -v  " + path + "%03G" %
               (current_banks + 1) + "_BANK", shell=True, check=True)
sys.exit(current_banks + 1)
