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
    strings.append ("%03G"% i)
print(strings)


def fs_tree_to_dict(path_):
    file_token = ''
    for root, dirs, files in os.walk(path_):
        tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
        tree.update({f: file_token for f in files})
        return tree  # note we discontinue iteration trough os.walk
 
tree  = fs_tree_to_dict(path)
for folder in tree:
    print(type(tree[folder]))
    if(isinstance(tree[folder], dict)):
        files = list(tree[folder])
        for wanted in strings:
            result = [v for v in files if wanted in v]
            if (len(result) > 1):
                match = [v for v in result if blank in v]
                print(match)
                for file in match:
                    path_to_file = path + folder + "/" + file
                    print(path_to_file) 
                    os.remove(path_to_file)
                
        #print (files) 
end=time.time()
print(end - start)
