import numpy as np
import subprocess
import os
import time
import sys
import re


start = time.time()
print("python:")
path = "/udata/nina/presets/patches/"
source_path = "/tmp/nina_bank_import/"
waves_path = "/udata/nina/wavetables/"

files = []
direcs = []

n = len(sys.argv)
print("Total arguments passed:", n)
if (n > 1):
    dest = sys.argv[1]
    print(dest)
    dest_num = dest[:3]
    print("dest num " + dest_num)
    
    rename = sys.argv[2]
    print(rename) 
    rename = re.search('nina_bank_(.*).zip',rename,re.I).group(1)
    print("bank rename  " + str(rename))

files_in_dst_dir = []
patches_in_source_dir = []

# copy all the wavetables from the imported bank to the wavetable folder, add all json files in the import bank to the list
for r, d, f in os.walk(source_path):
    for file in f:
        if '.wav' in file:
            print("import wave: " + file)
            subprocess.run("cp " + os.path.join(r, file) +
                           " " + waves_path, shell=True, check=True)
        if file.endswith('.json'):
            patches_in_source_dir.append(file)
            print("import patch: " + file)

print("dest files: " + path + dest + "/")
# find all the patches in the dest bank
for r, d, f in os.walk(path + dest + "/"):
    for file in f:
        if file.endswith('.json'):
            files_in_dst_dir.append(file)
            print(file)

# get the patch numbers
file_nums_in_dst = []
for name in files_in_dst_dir:
    file_nums_in_dst.append(name[0:3])
file_nums_in_src = []
for name in patches_in_source_dir:
    file_nums_in_src.append(name[0:3])

# delete patch numbers in dst bank that have matching numbers in the source
files_to_delete = []
for src_file in file_nums_in_src:
    files_to_delete.append([v for v in files_in_dst_dir if src_file in v])
print("delete:")
print(files_to_delete)

for src_file in files_to_delete:
    for item in src_file:
        os.system("rm " + path + dest + "/" + item)

# now copy all source json files to dest

print("cp " + source_path + "*.json" + " " + path + dest + "/")
subprocess.run("cp " + source_path + "*.json" + " " +
               path + dest + "/", shell=True, check=True)
subprocess.run("mv " + path + dest + " " + path +dest_num + "_"+   rename + " ", shell=True)
end = time.time()
print(end - start)
