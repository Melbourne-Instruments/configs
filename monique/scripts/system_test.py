import os
import numpy as np
import copy
import csv
import pickle
import platform

cpu = platform.machine()
print(cpu)
RUN_NATIVE = False
if cpu == "x86_64":
    RUN_NATIVE = True
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
working_dir = "/home/root/delia/scripts/"
presets_dir = "/udata/delia/presets/"
presets_refererence_file = "/home/root/delia/scripts/factory_preset_list.txt"

# local files
if RUN_NATIVE:
    working_dir = "./monique/scripts/"
    presets_dir = "/home/connor/dev/mon_presets_test/"
    presets_refererence_file = "./monique/scripts/factory_preset_list.txt"


def check_wavetables_against_reference():
    res = True
    wavetables = [
            "Harmonics.wav",
            "Inceptor.wav",
            "Rapid_Fire.wav",
            "Tri_Sqr_Morph.wav",
            "WT_80s_00.wav",
            "WT_80s_01.wav",
            "WT_80s_02.wav",
            "WT_80s_03.wav",
            "WT_80s_04.wav",
            "WT_80s_05.wav",
            "WT_80s_06.wav",
            "WT_80s_07.wav",
            "WT_80s_08.wav",
            "WT_80s_09.wav",
            "WT_80s_10.wav",
            "WT_80s_11.wav",
            "WT_80s_12.wav",
            "WT_80s_13.wav",
            "WT_80s_14.wav",
            "WT_80s_15.wav",
            "WT_80s_16.wav",
            "WT_80s_17.wav",
            "WT_80s_18.wav",
            "WT_80s_19.wav",
            "WT_80s_20.wav",
            "WT_80s_21.wav",
            "WT_80s_22.wav",
            "WT_80s_23.wav",
            "WT_80s_24.wav",
            "WT_80s_25.wav",
            "WT_80s_26.wav",
            "WT_80s_27.wav",
            "WT_80s_28.wav",
            "WT_80s_29.wav",
            "WT_80s_30.wav",
            "WT_80s_31.wav",
            "WT_SINE.wav",
            "Wavetable32_0.wav",
            "Wavetable32_1.wav",
            "Wavetable32_10.wav",
            "Wavetable32_11.wav",
            "Wavetable32_12.wav",
            "Wavetable32_13.wav",
            "Wavetable32_14.wav",
            "Wavetable32_15.wav",
            "Wavetable32_2.wav",
            "Wavetable32_3.wav",
            "Wavetable32_4.wav",
            "Wavetable32_5.wav",
            "Wavetable32_6.wav",
            "Wavetable32_7.wav",
            "Wavetable32_8.wav",
            "Wavetable32_9.wav"]
    
    if RUN_NATIVE:
        return True
    wavetable_dir = "/udata/delia/wavetables/"
    for path, dirs, files in os.walk(wavetable_dir):
        break

    # check for empty files
    for file in files:
        if os.path.getsize(wavetable_dir + file) == 0:
            return False
    files = sorted(files)
    run_wt_list_gen = False
    
    # uncomment to generate the wt list
    #run_wt_list_gen = True
    if run_wt_list_gen:
        print("\n [", end="\n")
        for item in files[:-1]:
            print('"' + item + '", ', end="\n")
        print('"' + files[-1] + '"', end="\n")
        print(" ]")

    res = files == wavetables
    return res


def check_presets_against_reference():
    # Read the current state of the preset directory, and compare this again the reference preset & bank list
    presets_file_order = []
    path = ""
    dirs = ""
    files = ""
    for path, dirs, files in os.walk(presets_dir):
        break
    presets_file_order = copy.deepcopy(dirs)
    for bank in dirs:

        for path_b, dirs_b, files_b in os.walk(presets_dir + "/" + bank):
            break

        # check for empty files
        for file in files_b:
            if os.path.getsize(presets_dir + bank + "/" + file) == 0:
                return False
        if files_b != []:
            presets_file_order = presets_file_order + files_b
    presets_file_order = sorted(presets_file_order)

    # uncomment to  generate preset test file
    # with open(presets_refererence_file, 'w') as f:
    #     for line in presets_file_order:
    #         f.write("%s\n" % line)

    # load reference preset list
    with open(presets_refererence_file) as f:
        lines = [line.rstrip("\n") for line in f]
        reference_list = lines

    match = reference_list == presets_file_order
    if not (match):
        for i in range(len(reference_list)):
            print(reference_list[i] + "\t\t\t" + presets_file_order[i])
    return match


tests_passed = True
disk_check = os.path.ismount("/media/")
if disk_check:
    log_location = "/media/system_test_error.txt"
else:
    log_location = "/udata/delia/system_test_error.txt"
try:
    os.remove(log_location)
except OSError:
    print("log file doesn't exist yet")
    pass
if RUN_NATIVE:
    log_location = "./system_test_error.txt"
# check that all the wavetables exist
res = False
try:
    res = check_wavetables_against_reference()
except:
    tests_passed = False
    print("check wavetable error " + str(res))
    with open(log_location, "a") as f:
        f.write("\n wavetable check error")
if not (res):
    tests_passed = False
    print("check wavetable error " + str(res))
    with open(log_location, "a") as f:
        f.write("\n wavetable files missing/incorrect")


# check various other files exist.
try:
    os.path.isdir("/udata/delia")
except OSError:
    tests_passed = False
    with open(log_location, "a") as f:
        f.write("\n udata/delia doesn't exist")
try:
    os.path.isdir("/udata/delia/calibration")
except OSError:
    tests_passed = False
    with open(log_location, "a") as f:
        f.write("\n udata/delia/calibration doesn't exist")
try:
    os.path.isdir("/udata/delia/presets")
except OSError:
    tests_passed = False
    with open(log_location, "a") as f:
        f.write("\n udata/delia/presets doesn't exist")
try:
    os.path.isdir("/udata/delia/tuning")
except OSError:
    tests_passed = False
    with open(log_location, "a") as f:
        f.write("\n udata/delia/tuning doesn't exist")
# try:
#     os.path.isfile("/udata/delia/presets/001_BANK/001_FACTORY_TEST.json")
#     assert os.path.getsize("/udata/delia/presets/001_BANK/001_FACTORY_TEST.json") > 0
# except:
#     tests_passed = False
#     with open(log_location, "a") as f:
#         f.write("\n factory test preset doesnt exist")
try:
    os.path.isfile("/udata/delia/config.json")
    assert os.path.getsize("/udata/delia/config.json") > 0
except:
    tests_passed = False
    with open(log_location, "a") as f:
        f.write("\n config.json doesn't exist")
try:
    os.path.isfile("/udata/delia/global_params.json")
    assert os.path.getsize("/udata/delia/global_params.json") > 0
except:
    tests_passed = False
    with open(log_location, "a") as f:
        f.write("\n global_params.json doesn't exist")
ret = 1
if tests_passed:
    ret = 0
exit(ret)
