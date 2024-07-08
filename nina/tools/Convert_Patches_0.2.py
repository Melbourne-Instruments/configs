import sys
import os
import re
from glob import glob

header = "{\n    \"version\": \"0.2\",\n    \"common\": [\n"
common_params = ["/cmn/tempo_bpm",
                 "/cmn/tempo_note_value",
                 "/cmn/hold",
                 "/daw/main/gain",
                 "/daw/main/pan",
                 "/daw/main/gain_sub_1",
                 "/daw/main/pan_sub_1",
                 "/daw/main/gain_sub_2",
                 "/daw/main/pan_sub_2",                 
                 "/daw/main/gain_sub_3",
                 "/daw/main/pan_sub_3",
                 "/daw/main/gain_sub_4",
                 "/daw/main/pan_sub_4",
                 "/daw/main/gain_sub_5",
                 "/daw/main/pan_sub_5",
                 "/daw/main/gain_sub_6",
                 "/daw/main/pan_sub_6",
                 "/daw/main/gain_sub_7",
                 "/daw/main/pan_sub_7",
                 "/daw/main/gain_sub_8",
                 "/daw/main/pan_sub_8",
                 "/daw/main/gain_sub_9",
                 "/daw/main/pan_sub_9",
                 "/daw/main/gain_sub_10",
                 "/daw/main/pan_sub_10",
                 "/daw/main/gain_sub_11",
                 "/daw/main/pan_sub_11",
                 "/daw/main/gain_sub_12",
                 "/daw/main/pan_sub_12",
                 "/daw/main/gain_sub_13",
                 "/daw/main/pan_sub_13",
                 "/daw/main/gain_sub_14",
                 "/daw/main/pan_sub_14",
                 "/daw/main/gain_sub_15",
                 "/daw/main/pan_sub_15",
                 "/daw/main/gain_sub_16",
                 "/daw/main/pan_sub_16",
                 "/daw/main/gain_sub_17",
                 "/daw/main/pan_sub_17",
                 "/daw/main/ninavst/Layer_State",
                 "/daw/main/ninavst/WT_Select",
                 "/daw/main/ninavst/Unison",
                 "/daw/main/ninavst/Unison_Spread",
                 "/daw/main/ninavst/Unison_Pan",
                 "/daw/main/ninavst/Legato",
                 "/daw/main/ninavst/Morph",
                 "/daw/main/ninavst/Spread_Amount",
                 "/daw/main/ninavst/Mod_Wheel",
                 "/daw/main/ninavst/Sustain",                 
                 "/daw/main/ninavst/Run_Tuning",
                 "/daw/main/ninavst/vca_offset_1",
                 "/daw/main/ninavst/vca_offset_2",
                 "/daw/main/ninavst/vca_offset_3",
                 "/daw/main/ninavst/vca_offset_4",
                 "/daw/main/ninavst/vca_offset_5",
                 "/daw/main/ninavst/vca_left_offset",
                 "/daw/main/ninavst/vca_right_offset",
                 "/daw/main/ninavst/filter_offset",
                 "/daw/main/ninavst/filter_scale",
                 "/daw/main/ninavst/filter_t_track",
                 "/daw/main/ninavst/voice_select",
                 "/daw/main/ninavst/voice_cal_write",
                 "/daw/main/ninavst/res_high_cal",
                 "/daw/main/ninavst/res_low_cal",
                 "/daw/main/ninavst/Tuning_Gain",
                 "/seq/enable",
                 "/arp/enable",
                 "/arp/dirmode",
                 "/daw/effects/gain",
                 "/daw/effects/pan",
                 "/daw/effects/effectsvst/LFO_1",
                 "/daw/effects/effectsvst/LFO_2",
                 "/daw/effects/effectsvst/Mode",
                 "/daw/effects/effectsvst/Vol"]
state_base_params = ["/daw/main/ninavst/VCO_1_Tune_Fine",
                     "/daw/main/ninavst/VCO_1_Tune_Coarse",
                     "/daw/main/ninavst/VCO_2_Tune_Fine",
                     "/daw/main/ninavst/VCO_2_Tune_Coarse",
                     "/daw/main/ninavst/Wave_Tune_Fine",
                     "/daw/main/ninavst/Wave_Tune_Coarse",
                     "/daw/main/ninavst/LFO_Shape",
                     "/daw/main/ninavst/VCF_Drive",
                     "/daw/main/ninavst/VCF_Overdrive",
                     "/daw/main/ninavst/VCF_Key_Track",
                     "/daw/main/ninavst/Glide",
                     "/daw/main/ninavst/Sub_Osc",
                     "/daw/main/ninavst/Hard_Sync"]
state_mod_matrix_src = ["Constant",
                        "LFO_1",
                        "LFO_2",
                        "Filter_Envelope",
                        "Amp_Envelope",
                        "Key_Velocity",
                        "Key_Pitch",
                        "Aftertouch",
                        "Pan_Position",
                        "Time"]
state_mod_matrix_dst = ["LFO_1_Rate",
                        "LFO_1_Gain",
                        "LFO_2_Rate",
                        "LFO_2_Gain",
                        "VCA_In",
                        "Pan",
                        "OSC_1_Pitch",
                        "OSC_1_Width",
                        "OSC_1_Blend",
                        "OSC_1_Level",
                        "OSC_2_Pitch",
                        "OSC_2_Width",
                        "OSC_2_Blend",
                        "OSC_2_Level",
                        "OSC_3_Pitch",
                        "OSC_3_Shape",
                        "OSC_3_Level",
                        "XOR_Level",
                        "Filter_Cutoff",
                        "Filter_Resonance",
                        "VCF_Attack",
                        "VCF_Decay",
                        "VCF_Sustain",
                        "VCF_Release",
                        "VCF_Level",
                        "VCA_Attack",
                        "VCA_Decay",
                        "VCA_Sustain",
                        "VCA_Release",
                        "VCA_Level",
                        "Spin_Rate"]
state_mod_matrix_alt = {
    "/daw/main/ninavst/Mod_Constant:LFO_1_Rate": "/daw/main/ninavst/LFO_1_Rate",
    "/daw/main/ninavst/Mod_Constant:LFO_1_Gain": "/daw/main/ninavst/LFO_1_Mod",
    "/daw/main/ninavst/Mod_Constant:OSC_1_Width": "/daw/main/ninavst/VCO_1_Width",
    "/daw/main/ninavst/Mod_Constant:OSC_1_Blend": "/daw/main/ninavst/VCO_1_Blend",
    "/daw/main/ninavst/Mod_Constant:OSC_1_Level": "/daw/main/ninavst/Mix_VCO_1",
    "/daw/main/ninavst/Mod_Constant:OSC_2_Width": "/daw/main/ninavst/VCO_2_Width",
    "/daw/main/ninavst/Mod_Constant:OSC_2_Blend": "/daw/main/ninavst/VCO_2_Blend",
    "/daw/main/ninavst/Mod_Constant:OSC_2_Level": "/daw/main/ninavst/Mix_VCO_2",
    "/daw/main/ninavst/Mod_Constant:OSC_3_Shape": "/daw/main/ninavst/Wave_Shape",
    "/daw/main/ninavst/Mod_Constant:OSC_3_Level": "/daw/main/ninavst/Mix_Wave",
    "/daw/main/ninavst/Mod_Constant:XOR_Level": "/daw/main/ninavst/Mix_XOR",
    "/daw/main/ninavst/Mod_Constant:Filter_Cutoff": "/daw/main/ninavst/VCF_Cutoff",
    "/daw/main/ninavst/Mod_Constant:Filter_Resonance": "/daw/main/ninavst/VCF_Resonance",
    "/daw/main/ninavst/Mod_Constant:VCF_Attack": "/daw/main/ninavst/VCF_Attack",
    "/daw/main/ninavst/Mod_Constant:VCF_Decay": "/daw/main/ninavst/VCF_Decay",
    "/daw/main/ninavst/Mod_Constant:VCF_Sustain": "/daw/main/ninavst/VCF_Sustain",
    "/daw/main/ninavst/Mod_Constant:VCF_Release": "/daw/main/ninavst/VCF_Release",
    "/daw/main/ninavst/Mod_Constant:VCA_Attack": "/daw/main/ninavst/VCA_Attack",
    "/daw/main/ninavst/Mod_Constant:VCA_Decay": "/daw/main/ninavst/VCA_Decay",
    "/daw/main/ninavst/Mod_Constant:VCA_Sustain": "/daw/main/ninavst/VCA_Sustain",
    "/daw/main/ninavst/Mod_Constant:VCA_Release": "/daw/main/ninavst/VCA_Release",
    "/daw/main/ninavst/Mod_Constant:Spin_Rate": "/daw/main/ninavst/Spin_Rate",
    "/daw/main/ninavst/Mod_Filter_Envelope:Filter_Cutoff": "/daw/main/ninavst/VCF_Env_Mod"
}
old_mod_matrix_src_indexes = {
    2: 1,       # LFO 1
    4: 2,       # Filter Envelope
    5: 3,       # Amp Envelope
    6: 4,       # Key Velocity
    1: 5,       # Constant
    7: 6        # Key Pitch
}
old_mod_matrix_dst_indexes = {
    19: 1,      # Filter Cutoff
    20: 2,      # Filter Resonance
    7:  3,      # OSC 1 Tune
    8:  4,      # OSC 1 Width
    11: 5,      # OSC 2 Tune
    12: 6,      # OSC 2 Width
    15: 7,      # OSC 3 Tune
    16: 8,      # OSC 3 Width
    1:  9,      # LFO 1 Rate
    2:  10,     # LFO 1 Amount
    5:  12,     # VCA In 
}
param_alt_path = {
    "/daw/main/synthiavst/LFO_1_Rate": "/daw/main/synthiavst/LFO_Rate",
    "/daw/main/synthiavst/LFO_1_Mod": "/daw/main/synthiavst/LFO_Mod"
}
param_value_overwrite = {
    "/daw/main/ninavst/Mod_Constant:VCA_In": "0.5",
    "/daw/main/ninavst/Mod_Constant:VCF_Level": "1.0",
    "/daw/main/ninavst/Mod_Constant:VCA_Level": "1.0",
    "/daw/main/ninavst/Mod_Amp_Envelope:VCA_In": "1.0",
    "/daw/main/ninavst/Mod_Key_Pitch:OSC_1_Pitch": "1.0",
    "/daw/main/ninavst/Mod_Key_Pitch:OSC_2_Pitch": "1.0",
    "/daw/main/ninavst/Mod_Constant:LFO_2_Gain": "0.0",
    "/daw/main/ninavst/VCO_1_Tune_Coarse": "0.5",
    "/daw/main/ninavst/VCO_2_Tune_Coarse": "0.5",
    "/daw/main/ninavst/Wave_Tune_Coarse": "0.5"
} 

def get_val(lines, param_path):
    found = False
    for l in lines:
        l = l.strip()
        if found:
            return l
        if param_path == l:
            found = True
    return ""

def process_patch(f):
    # Read in the current file contents
    old_lines = f.readlines()
    if len(old_lines) < 2:
        print("Invalid patch file format: " + f.name)
        return False

    # Get the current patch version (assumed to always be in the second line)
    ver = re.findall("\d+\.\d+",old_lines[1])
    if len(ver) != 1:
        print("Invalid patch file format: " + f.name)
        return False
    # Only allow older files to be converted
    if float(ver[0]) == 0.2:
        print("Patch file is current version (" + ver[0] + "): " + f.name)
        return False
    if float(ver[0]) > 0.2:
        print("Patch file is newer version (" + ver[0] + "): " + f.name)
        return False

    # Clear the file contents, write the header
    f.truncate(0)
    f.seek(0)
    f.writelines(header)        

    # Common params
    print(f.name)
    vcf_key_track = 0.0
    for p in common_params:
        path = "\"path\": \"" + p + "\","
        path_line = "        {\n            " + path + "\n"
        val_line = get_val(old_lines, path.replace("/ninavst/", "/synthiavst/"))
        if val_line == "":
            val_line = "\"value\": 0.0\n"
        if p == common_params[-1]:
            val_line = "            " + val_line + "\n        }\n"
        else:
            val_line = "            " + val_line + "\n        },\n"
        f.write(path_line)
        f.write(val_line)

    # State A params
    f.write("    ],\n    \"state_a\": [\n")
    state_lines = []
    for p in state_base_params:
        path = "\"path\": \"" + p + "\","
        path_line = "        {\n            " + path + "\n"
        val_overwrite = param_value_overwrite.get(p)
        if val_overwrite != None:
            v = "\"value\": " + val_overwrite
        else:        
            v = get_val(old_lines, path.replace("/ninavst/", "/synthiavst/"))
            if v == "":
                v = "\"value\": 0.0"
        val_line = "            " + v + "\n        },\n"
        # If this is key track, save the actual value
        if p == "/daw/main/ninavst/VCF_Key_Track":
            vcf_key_track = float(v.split(":")[1])
        f.write(path_line)
        f.write(val_line)            
        state_lines.append(path_line)
        state_lines.append(val_line)
    i = 1
    for s in state_mod_matrix_src:
        j = 1
        for d in state_mod_matrix_dst:
            path = "/daw/main/ninavst/Mod_" + s + ":" + d
            old_path = ""
            alt_path = state_mod_matrix_alt.get(path)         
            if alt_path != None:
                path = alt_path
                old_path = path.replace("/ninavst/", "/synthiavst/")
            else:
                old_src_index = old_mod_matrix_src_indexes.get(i)
                old_dst_index = old_mod_matrix_dst_indexes.get(j)
                if old_src_index != None and old_dst_index != None:
                    old_path = "/daw/main/synthiavst/mod_src_" + str(old_src_index) + "_dst_" + str(old_dst_index)
            full_path = "\"path\": \"" + path + "\","
            path_line = "        {\n            " + full_path + "\n"
            val_line = ""
            val_overwrite = param_value_overwrite.get(path)
            if val_overwrite != None:
                val_line = "\"value\": " + val_overwrite
            else:
                if old_path != "":
                    alt_path = param_alt_path.get(old_path)
                    if alt_path != None:
                        old_path = alt_path
                    old_full_path = "\"path\": \"" + old_path + "\","
                    val_line = get_val(old_lines, old_full_path)
                if val_line == "":
                    val_line = "\"value\": 0.5"
                # Special cases for Key Track
                if path == "/daw/main/ninavst/Mod_Key_Pitch:Filter_Cutoff":
                    if vcf_key_track > 0.5:
                        val_line = "\"value\": 0.55"
                if path == "/daw/main/ninavst/VCF_Cutoff":
                    if vcf_key_track > 0.5:
                        val = float(val_line.split(":")[1]) + 0.5
                        if val > 1.0:
                            val = 1.0
                        val_line = "\"value\": " + str(val)                  
            if s == state_mod_matrix_src[-1] and d == state_mod_matrix_dst[-1]:
                val_line = "            " + val_line + "\n        }\n"
            else:
                val_line = "            " + val_line + "\n        },\n"
            f.write(path_line)
            f.write(val_line)
            state_lines.append(path_line)
            state_lines.append(val_line)
            j += 1
        i += 1                         

    # State B params (same as State A)
    f.write("    ],\n    \"state_b\": [\n")
    for l in state_lines:
        f.write(l)
    f.write("    ]\n}\n")
    return True

list_folders = [x[0] for x in os.walk("./patches")]
if len(list_folders) == 0:
    print("Patches folder not found - all patches must be under a 'patches' sub-folder")
    sys.exit()
list_json = [y for x in os.walk("./patches") for y in glob(os.path.join(x[0], '*.json'))]
if len(list_json) == 0:
    print("No patches found")
    sys.exit()

# Process each patch file
for file in list_json:
    with open(file,"r+") as f:
        processed = process_patch(f)
        f.close()
        if processed:
            file_split = file.split("/")
            if file_split[2] != "default.json":
                index = file_split[3].split("_")[0]
                if len(index) == 2 and index.isnumeric():
                    file_split[3] = '0' + file_split[3]
                    new_file = "/".join(file_split)
                    os.rename(file, new_file)

# Rename each folder if required
list_folders.pop(0)
for folder in list_folders:
    folder_split = folder.split("/")
    index = folder_split[2].split("_")[0]
    if len(index) == 2 and index.isnumeric():
        folder = "/".join(folder_split)
        folder_split[2] = '0' + folder_split[2]
        new_folder = "/".join(folder_split)
        print(folder, new_folder)
        os.rename(folder, new_folder)
