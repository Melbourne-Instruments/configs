import numpy as np
import json
import os
import time

start = time.time()
path = "/udata/nina/presets/patches/"
files = []

# find all json files in directory
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if file.endswith('.json'):
            files.append(os.path.join(r, file))


def getParam(json_object, name):
    return [obj for obj in json_object if obj['path'] == name]


for file in files:
    print(file)
    f = open(file)
    try:
        data = json.load(f)
    except:
        print("bung file")
        data = {"version": -1}
    version = data["version"]
    file_updated = False

    # updates for version 0.2
    if(data["version"] == "0.2"):
        print("0.3 update")
        for section in data.keys():
            if((section == "state_a") | (section == "state_b")):
                state = data[section]
                # update velocity sense scaling
                item = getParam(
                    state, "/daw/main/ninavst/Amp_Env_Velocity_Sense")[0]
                print(item)
                item["value"] = (item["value"])/2 + 0.5
                item = getParam(
                    state, "/daw/main/ninavst/Filt_Env_Velocity_Sense")[0]
                print(item)
                item["value"] = (item["value"])/2 + 0.5

                # set the default pan amount to give an LR spread with no antiphase
                item = getParam(
                    state, "/daw/main/ninavst/Mod_Pan_Position:Pan")[0]
                print(item)
                item["value"] = 0.5 + 0.125
                item = getParam(
                    state, "/daw/main/ninavst/Mod_Key_Pitch:Pan")[0]
                print(item)
                item["value"] = np.clip(item["value"]*4, -1, 1)

                print(item)
                # update the patch version number
                data["version"] = "0.3"

    # updates for version 0.3 go here
    if (data["version"] == "0.3"):
        print("run 0.3.1 update")
        file_updated = True

        for section in data.keys():
            section_data = data[section]
            if(isinstance(section_data, list)):
                items = [obj for obj in section_data if "gain" in obj['path']]
                for item in items:
                    section_data.remove(item)
                items = [obj for obj in section_data if "pan" in obj['path']]
                for item in items:
                    section_data.remove(item)
                    # section_data.remove(item)
        data["version"] = "0.3.1"

    if (data["version"] == "0.3.1"):
        print("run 0.3.2 update")
        file_updated = True

        for section in data.keys():
            section_data = data[section]
            if(isinstance(section_data, list)):
                items = [
                    obj for obj in section_data if "/seq/enable" in obj['path']]
                for item in items:
                    print(item)
                    section_data.remove(item)
                items = [
                    obj for obj in section_data if "/seq/num_steps" in obj['path']]
                for item in items:
                    print(item)
                    section_data.remove(item)
                    # section_data.remove(item)
        data["version"] = "0.3.2"

    if (data["version"] == "0.3.2"):
        print("run 0.3.3 update")
        file_updated = True

        for section in data.keys():
            section_data = data[section]
            if(isinstance(section_data, list)):
                items = [
                    obj for obj in section_data if "wt_name" in obj['path']]
                for item in items:
                    print(item)
                    if (item["str_value"] == ""):
                        item["str_value"] = "WT_80s_00"
        data["version"] = "0.3.3"

    if (data["version"] == "0.3.3"):
        print("run 0.3.4 update")
        file_updated = True

        for section in data.keys():
            section_data = data[section]
            if(isinstance(section_data, list)):
                items = [
                    obj for obj in section_data if "_Retrigger" in obj['path']]
                for item in items:
                    item["value"] *= 2/3 
                items = [
                    obj for obj in section_data if "Time_Rate" in obj['path']]
                for item in items:
                    if item["value"] < 0.01:
                        item["value"] = 0.25
                         
        data["version"] = "0.3.4"

    print("up to date")
    # file is up to date, save file

    if(file_updated == True):
        with open(file, 'w') as output:
            json.dump(data, output, indent=4)
            print("done, save file")
        #print("file update failed")
end = time.time()
print(end - start)
