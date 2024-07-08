import numpy as np
import json
import os
import time

start = time.time()
path = "/udata/nina/presets/patches/"
path = "./"
files = []

# find all json files in directory
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if file.endswith('.json'):
            files.append(os.path.join(r, file))

#files = ["./nina/nina_ui/011_BLANK.json"]

def getParam(json_object, name):
    return [obj for obj in json_object if obj['path'] == name]


for file in files:
    print("file  " +  file)
    f = open(file)
    try:
        data = json.load(f)
    except:
        print("bung file")
        data = {"version": -1}
    version = data["version"]

    
    for section in data.keys():
        section_data = data[section]
        if(isinstance(section_data, list)):
            items = [obj for obj in section_data if "Mod_" in obj['path']]
            if(len(items) >0):
                for item in items:
                    if(abs(item["value"]-0.5) < (0.5/700)):
                        section_data.remove(item)
                        print(item)


    with open(file, 'w') as output:
        json.dump(data, output, indent=4)
        print("done, save file")
end = time.time()
print(end - start)
