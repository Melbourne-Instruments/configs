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
check = True

n = len(sys.argv)
print("Total arguments passed:", n)
if (n > 1):
    dest = sys.argv[2]
    print(dest)
    check = sys.argv[1] == 'check'
print("run check: " + str(check))


files_in_dst_dir = []
patches_in_source_dir = []

# find all the source patches and sort them
for r, d, f in os.walk(source_path):
    for file in f:
        if file.endswith('.json'):
            patches_in_source_dir.append(file)

patches_in_source_dir.sort(key=str.lower)
print("src files: ")
print(patches_in_source_dir)

# find all the dest patches
print("dest files: " + path + dest + "/")
blank_slots = []
# find all the patches in the dest bank
for r, d, f in os.walk(path + dest + "/"):
    for file in f:
        if file.endswith('.json'):
            files_in_dst_dir.append(file)

# only keep names that are not BLANK.json
files_in_dst_dir = ([file for file in (files_in_dst_dir)
                    if not (re.search('\d{3}_BLANK\.json', file))])
print(files_in_dst_dir)

#remove patches from the source list if the names conflict with a patch already in the target bank
conflicting_patches = []
for src_patch in patches_in_source_dir:
    print (src_patch)
    src_patch = src_patch[4:]
    print (src_patch)
    matches = ([file for file in (files_in_dst_dir) if src_patch in file])
    print(matches)
    if(len(matches) > 0):
        conflicting_patches.append(src_patch)
        print ("remove " + src_patch) 
print("remove these:")
print(conflicting_patches)
for remove_me in conflicting_patches:
    for item in patches_in_source_dir:
        if(remove_me in item):
            patches_in_source_dir.remove(item)
patches_in_source_dir = list(patches_in_source_dir)
print(patches_in_source_dir)

#if there are no patches left to add, we just exit    
print(patches_in_source_dir)
print("leftover patches to add: ")
if(len(list(patches_in_source_dir)) < 1):
    print("nothing to copy")
    sys.exit(0)

# compare the files to a full bank number set. remove any slots already taken
spare_slots = []
for i in range(127):
    spare_slots.append("%03G" % (i + 1))
print(spare_slots)
for file in files_in_dst_dir:
    print("file: " + file)
    spare_slots.remove(file[0:3])
print("availiable locations: ")
print(spare_slots)
print(patches_in_source_dir)

# exit if there are insufficient patch slots availiable. also exit if we are just running the check option
if (len(patches_in_source_dir) > len(spare_slots)):
    print("not enough free patches")
    sys.exit(1)
elif (check):
    print("Pass")
    sys.exit(0)


for source_patch in patches_in_source_dir:
    dst_slot = spare_slots[0]
    spare_slots.pop(0)
    print(source_patch + " copy to " + dst_slot)

    # remove any possible file at the slot location
    print("rm -f " + path + dest + "/" + dst_slot + "*")
    subprocess.run("rm  -f " + path + dest + "/" +
                   dst_slot + "*", shell=True, check=True)
    print("cp -v " + source_path + source_patch + " " +
          path + dest + "/" + dst_slot + source_patch[3:])
    subprocess.run("cp -v " + source_path + source_patch + " " + path +
                   dest + "/" + dst_slot + source_patch[3:], shell=True, check=True)

# copy all the wavetables from the imported bank to the wavetable folder
for r, d, f in os.walk(source_path):
    for file in f:
        if '.wav' in file:
            print("import wave: " + file)
            subprocess.run("cp -v " + os.path.join(r, file) +
                           " " + waves_path, shell=True, check=True)

end = time.time()
print(end - start)
