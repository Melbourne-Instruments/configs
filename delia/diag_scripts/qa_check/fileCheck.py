import os
import numpy as np
import copy
import sys

presets_dir = "/udata/delia/presets/"
presets_refererence_file = "/media/factory_preset_list.txt"
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

    # load reference preset list
    with open(presets_refererence_file) as f:
        lines = [line.rstrip("\n") for line in f]
        reference_list = lines

    match = reference_list == presets_file_order
    if not (match):
        for i in range(len(reference_list)):
            print(reference_list[i] + "\t\t\t" + presets_file_order[i])
    return match

class Run_Test:
    WAVE = 0
    PRESETS = 1
    SYSTEM = 2

run_test = Run_Test.SYSTEM
# arguments
n = len(sys.argv)
print("start")
print("Total arguments passed:", n)
if(n > 1):
    val = sys.argv[1]
    print(val)

    if("wt" in sys.argv[1]):
        run_test = Run_Test.WAVE
    if("preset" in sys.argv[1]):
        run_test = Run_Test.PRESETS
    if("sys" in sys.argv[1]):
        run_test = Run_Test.SYSTEM
    
if(run_test == Run_Test.WAVE):
    # check that all the wavetables exist
    res = False
    try:
        res = check_wavetables_against_reference()
    except:
        print("check wavetable error " + str(res))
        exit(-1)
    if not (res):
        print("check wavetable error " + str(res))
        exit(1)
    exit(0)
    
if(run_test == Run_Test.PRESETS):
    # check that all the wavetables exist
    res = False
    try:
        res = check_presets_against_reference()
    except:
        print("check presets error " + str(res))
        exit(-1)
    if not (res):
        print("check presets error " + str(res))
        exit(1)
    exit(0)
    
    
if(run_test == Run_Test.SYSTEM):
    tests_passed = False
    # check various other files exist.
    try:
        os.path.isdir("/udata/delia")
        tests_passed = True
    except OSError:
        tests_passed = False
        print("\n udata/delia doesn't exist")
    try:
        os.path.isdir("/udata/delia/calibration")
        tests_passed = True
    except OSError:
        tests_passed = False
        print("\n udata/delia/calibration doesn't exist")
    try:
        os.path.isdir("/udata/delia/presets")
        tests_passed = True
    except OSError:
        tests_passed = False
        print("\n udata/delia/presets doesn't exist")
    try:
        os.path.isdir("/udata/delia/tuning")
        tests_passed = True
    except OSError:
        tests_passed = False
        print("\n udata/delia/tuning doesn't exist")
    try:
        os.path.isfile("/udata/delia/config.json")
        assert os.path.getsize("/udata/delia/config.json") > 0
        tests_passed = True
    except:
        tests_passed = False
        print("\n config.json doesn't exist")
    try:
        os.path.isfile("/udata/delia/global_params.json")
        assert os.path.getsize("/udata/delia/global_params.json") > 0
        tests_passed = True
    except:
        tests_passed = False
        print("\n global_params.json doesn't exist")
    ret = 1
    if tests_passed:
        ret = 0
    exit(ret)
    
exit(-1)

