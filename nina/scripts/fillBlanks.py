import numpy as np
import json
import os
import time

start = time.time()
path = "/udata/nina/presets/patches/"
files = []
direcs = []

strings = []
blank = "BLANK.json"
for i in range(127):
    strings.append ("%03G"% (i + 1))
print(strings)

folder_strings = []
for i in range(32):
    folder_strings.append ("%03G"% (i+1))
print(folder_strings)

def fs_tree_to_dict(path_):
    file_token = ''
    for root, dirs, files in os.walk(path_):
        tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
        tree.update({f: file_token for f in files})
        return tree  # note we discontinue iteration trough os.walk

dirs = os.listdir(path) 
print(dirs)
for wanted in folder_strings:
        result = [v for v in dirs if wanted in v]
        print(result)
        if(len(result) == 0):
            dir_path = path + wanted + "_BANK"
            print(dir_path)
            os.system("mkdir " + dir_path)
                    
end=time.time()
print(end - start)
