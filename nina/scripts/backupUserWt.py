import numpy as np
import os
import time
import tarfile
import factoryWtList

factory_waves = factoryWtList.factory_waves

start = time.time()
path = "/udata/nina/wavetables"
tmp_backup_path = "/tmp/wt_backup"
files = []
direcs = []

os.system("rm -rf " + tmp_backup_path)
current_waves = os.listdir(path)
os.system("mkdir " + tmp_backup_path)
for wave in current_waves:
    print(wave)
    if(not(wave in factory_waves)):
        print("\t\t\t copy wt")
        os.system("cp " + path + "/\""+wave+"\"" + " " + tmp_backup_path + "/")
end = time.time()
print(end - start)
