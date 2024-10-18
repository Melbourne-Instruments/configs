import numpy as np
import os
import time
import tarfile
import subprocess


start = time.time()
path = "/udata/delia/presets/"
source_path = "/tmp/udata/delia/presets/"
files = []
direcs = []

strings = []
blank = "BLANK.json"
for i in range(127):
    strings.append("%03G" % (i + 1))
print(strings)

folder_strings = []
for i in range(31):
    folder_strings.append("%03G" % (i+1))
print(folder_strings)


def fs_tree_to_dict(path_):
    file_token = ''
    for root, dirs, files in os.walk(path_):
        tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
        tree.update({f: file_token for f in files})
        return tree  # note we discontinue iteration trough os.walk


source_dirs = os.listdir(source_path)
dst_dirs = os.listdir(path)


print(dst_dirs)
print(source_dirs)


for wanted in (source_dirs[:]):
    print("wanted" + wanted)
    wanted_trim = wanted[0:3]
    result = [v for v in dst_dirs if wanted_trim in v]
    print("result" + str(result))
    if (len(result) > 0):
        print("replace " + str(result) + " with " + str(wanted))
        subprocess.run("mv " + path + result[0] + " "+  path + wanted, shell=True)
    else:
        print("make bank dir: " + path+wanted)
        os.mkdir(path + wanted)
    print("dst files ")
    dst_files = os.listdir(path + wanted)
    src_files = os.listdir(source_path + wanted)
    print(dst_files)
    print("src files ")
    print(src_files)

    for file in src_files:
        file_trim = file[0:3]
        os.system("rm -f " + path + wanted + "/" + file_trim + "*")
        print("remove " + path + wanted + "/" + file_trim)
    print("")

    print("copy " + source_path + wanted + "/* to " + path + wanted + "/")
    os.system("cp " + source_path + wanted + "/* " + path + wanted + "/")

    print("")

end = time.time()
print(end - start)
