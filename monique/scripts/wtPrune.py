import json
import os
import time
import factoryWtList
import subprocess
import re

start = time.time()
path = "/udata/delia/presets/presets/"
waves_path = "/udata/delia/wavetables/"
files = []

# find all json files
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if file.endswith('.json'):
            files.append(os.path.join(r, file))


def getParam(json_object, name):
    return [obj for obj in json_object if obj['path'] == name]


used_waves = []
for file in files:
    print(file)
    f = open(file)
    try:
        data = json.load(f)
    except:
        print("bung file")

    for section in data.keys():
        section_data = data[section]
        if (isinstance(section_data, list)):
            items = [
                obj for obj in section_data if "wt_name" in obj['path']]
            for item in items:
                print(item)
                if (not (item in used_waves)):
                    used_waves.append(item)
print("detected waves: ")
for wave in used_waves:
    print(wave)
waves_names = []
waves = []

# find all json files in directory
# r=root, d=directories, f = files
for r, d, f in os.walk(waves_path):
    for file in f:
        waves.append(os.path.join(r, file))
        waves_names.append(file)
print("\n current waves: \n")
for wave in waves:
    print(wave)
delete_me = []

# get all waves that are not used in patches and are not in the factory list. match by name then get the path
delete_me = waves

#removes waves from the list that are used in a patch
for wave in used_waves:
    for check_wave in delete_me:
        if(wave['str_value'] in check_wave):
            delete_me.remove(check_wave)
            
#removes waves from the list that are in the factory list
for wave in factoryWtList.factory_waves:
    for check_wave in delete_me:
        if(wave in check_wave):
            delete_me.remove(check_wave)   
print("deleting: ")
for wave in delete_me:
    print(wave)
    subprocess.call("rm -v " + (wave), shell=True)

end = time.time()
print(end - start)