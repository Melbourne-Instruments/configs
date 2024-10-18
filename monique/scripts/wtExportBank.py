import json
import os
import time
import factoryWtList
import sys
import subprocess

start = time.time()
path = "/udata/delia/presets/"
waves_path = "/udata/delia/wavetables/"

exported_patches = "/tmp/"
files = []

n = len(sys.argv)
print("Total arguments passed:", n)
if (n > 1):
    sel_bank = sys.argv[1]
    print(sel_bank)

# find all json files
# r=root, d=directories, f = files
for r, d, f in os.walk(exported_patches + "delia_bank_" + sel_bank):
    for file in f:
        if file.endswith('.json'):
            files.append(os.path.join(r, file))


def getParam(json_object, name):
    return [obj for obj in json_object if obj['path'] == name]


# find all the wavetables used by the patches that are exported
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

                    # have to append .wav to the file for matching purposes
                    used_waves.append(item["str_value"] + ".wav")

print("used waves: ")
print(used_waves)
waves_names = []
waves = []

# make a list of all wavetables on DELIA
for r, d, f in os.walk(waves_path):
    for file in f:
        if '.wav' in file:
            waves.append(os.path.join(r, file))
            waves_names.append(file)
print("\n waves: \n")
print(waves_names)
backup_waves = []

# get all waves that are used in patches and are not in the factory list. match by name then get the path
for wave in waves_names:
    if not (wave in factoryWtList.factory_waves):
        print(wave + " not in factory")
        if ((wave in used_waves)):
            print("copy " + wave)
            backup_waves.append([x for x in waves if wave in x])

print(backup_waves)
# copy the used wavetables to the export directory
for wave in backup_waves:
    print(wave)
    subprocess.run("cp " + (wave[0]) + " " + exported_patches +
                   "delia_bank_" + sel_bank, shell=True, check=True)

end = time.time()
print(end - start)
