import numpy as np
import os
import time
import sys
import re
from scipy.io import wavfile as wload
import scipy.signal as sps
import wavfile

WAVEEDIT_WT_LENGTH = 256
WAVEEDIT_NUM_WAVES = 64
WAVEEDIT_TOTAL_SAMPLES = WAVEEDIT_WT_LENGTH * WAVEEDIT_NUM_WAVES

DELIA_WT_LENGTH = 2048
DELIA_MAX_WAVES = 256
DELIA_MAX_SAMPLES = DELIA_WT_LENGTH * DELIA_MAX_WAVES

MAX_SUPPORTED_WT_FILES = 127

def check_wave(path):
    try:
        try:
            wt_length = wavfile.read_wt_length(path)
            samplerate, wave_table = wavfile.read(path)
            shape = np.shape(wave_table)
            file_is_wave_edit_length = (shape[0] == WAVEEDIT_TOTAL_SAMPLES)
        except:
            print("load warning " + path)
        
        print(wt_length)
        #handle SERUM format
        if((wt_length == DELIA_WT_LENGTH or  not(file_is_wave_edit_length))):
            print("load serum wt")
            samplerate, wave_table = wavfile.read(path)
            shape = np.shape(wave_table)
            print(path)
            print("srate " + str(samplerate) + " len: " + str(np.shape(wave_table)))
            if(shape == (0,)):
                print("empty array")
                return False
            if(len(shape) > 1):
                print("too many channels")
                return False
            length = shape[0]
            if((length % DELIA_WT_LENGTH) != 0 ):
                print("wrong length")
                return False
            if((length / DELIA_WT_LENGTH) > DELIA_MAX_WAVES):
                print("wt too long")
                return False
            return True
        
        #handle WAVEEDIT format
        else:
            print("load waveedit wt")
            samplerate, wave_table = wload.read(path)
            shape = np.shape(wave_table)
            print(path)
            print("srate " + str(samplerate) + " len: " + str(np.shape(wave_table)))
            if(shape == (0,)):
                print("empty array")
                return False
            if(len(shape) > 1):
                print("too many channels")
                return False
            length = shape[0]
            
            #WAVEEDIT length should always be exactly 256 samples * 64 waves
            if(length != WAVEEDIT_TOTAL_SAMPLES):
                print("wrong length")
                return False
           
            #resample the waveedit file
            data = sps.resample_poly(wave_table,DELIA_WT_LENGTH/WAVEEDIT_WT_LENGTH,1)
            data = data /abs(np.max(np.abs(data)))
            data = data * ((np.iinfo(np.int16)).max)
            data = data.astype(np.int16)
            #replace file with resampled version
            wload.write(path,int(samplerate),data)
            print("check fixed file " + path)
            
            #check the resulting file using the serum checks
            samplerate, wave_table = wload.read(path)
            shape = np.shape(wave_table)
            print(path)
            print("srate " + str(samplerate) + " len: " + str(np.shape(wave_table)))
            if(shape == (0,)):
                print("empty array")
                return False
            if(len(shape) > 1):
                print("too many channels")
                return False
            length = shape[0]
            if((length % DELIA_WT_LENGTH) != 0 ):
                print("wrong length")
                return False
            if((length / DELIA_WT_LENGTH) > 256):
                print("wt too long")
                return False
            return True
    
    except:
        print("something bad with wave file")
        return False
    
start = time.time()
path = "/udata/delia/wavetables"
source_path = "/tmp/user_wavetables"
files = []
direcs = []

current_waves = os.listdir(path)
print(current_waves)

if (os.path.exists(source_path)):
    new_waves = os.listdir(source_path + "/")

    #remove all files that dont match the .wav pattern
    new_waves = ([file for file in (new_waves)
                  if (re.search('.*\.wav$', file,re.IGNORECASE))])

    #fix names
    for index, i in enumerate(new_waves):
        #detect whitespace
        item = new_waves[index]
        item_no_white = item.replace(" ", "_")
        
        #we dont handle '  " chars so also remove them
        item_no_white = item_no_white.replace("\'", "")
        item_no_white = item_no_white.replace("\"", "")

        
        if(item != item_no_white):
            wave_path =  source_path + "/" + item
            dst_path =  source_path + "/" + item_no_white
            os.system("mv -v " + "\"" + wave_path + "\"  \"" + dst_path +  "\" ")
            new_waves[index] = item_no_white
    
    #find files that are in both directories so we can avoid counting them
    no_count_waves = []
    for item in new_waves:
        if item in current_waves:
            no_count_waves.append(item)
    
    #exit if num wavetables will be over 127
    if ((len(current_waves) + len(new_waves) - len(no_count_waves)) > MAX_SUPPORTED_WT_FILES):
        print("too many wavetables")
        sys.exit(127)
    print("load user waves:")
    print(new_waves)
    
    #check each wave
    for item in new_waves:
        wave_path =  source_path + "/" + item
        res = check_wave(wave_path)
        if(not(res)):
            #write the name of the failed file to wavetable_error.txt for error display
            f = open("/tmp/wavetable_error.txt", "w+")
            f.write(item)
            f.close
            print("bad wave")
            sys.exit(-1)
    
    #copy each wave
    for item in new_waves:
        wave_path = "\"" + source_path + "/" + item + "\""
        
        #dst location, force wav name to lowercase for ui compatibility
        item = item.strip()
        dst_path = path + "/" + item[:-3] + "wav"
        res = os.WEXITSTATUS(os.system("cp -v " + "\"" + wave_path + "\" " + dst_path ))
        if(res):
            f = open("/tmp/wavetable_error.txt", "w+")
            f.write(item)
            f.close
            print("copy failed " + str(os.WEXITSTATUS()) )
            sys.exit(-1)
            
end = time.time()
print(end - start)
