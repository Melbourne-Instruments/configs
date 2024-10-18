import traceback
from elkpy import sushicontroller as sc
import numpy as np
import time
from datetime import datetime
import subprocess
import os

CAL_COMPLETE_FILE = "/udata/delia/tuning/cal_complete"
THRESH = 0.01

def deleteCalFile():
    try:
        os.remove(CAL_COMPLETE_FILE)
    except:
        print("file not yet created")
        
class voice_param(object):
    def __init__(self, name, param_id, value):
        self.name = name
        self.id = param_id
        self.value = value

    def __str__(self):
        return f'{self.name}, {self.id}, {self.value}'

    def __repr__(self):
        return f'[{self.name}, {self.id}, {self.value}]'


def make_voice_param(name, param_id, value):
    param = voice_param(name, param_id, value)
    return param


class interface(object):
    def __init__(self):
        self.controller = sc.SushiController()
        try:
            self.sushi_version = self.controller.system.get_sushi_version()
            self.processors = self.controller.audio_graph.get_all_processors()
            self.nina_process = None
            self.sampler_process = None
            self.sampler_trigger = None
            self.params = []
            self.temp_data = []
            self.start_time = datetime.now()
            for process in self.processors:
                print(process)
                if process.name == 'delia':
                    self.nina_process = process.id
                    print(self.nina_process)
            
            nina_params = self.controller.parameters.get_processor_parameters(
                self.nina_process)

            for param in nina_params:
                value = self.controller.parameters.get_parameter_value(
                    self.nina_process, param.id)
                if 'Cal' in param.name:
                    self.params.append(make_voice_param(
                        param.name, param.id, value))
                if 'Main Vca Cal' in param.name:
                    self.params.append(make_voice_param(
                        param.name, param.id, value))
                if 'Mix Vca Cal' in param.name:
                    self.params.append(make_voice_param(
                        param.name, param.id, value))
                if 'Filter Cal' in param.name:
                    self.params.append(make_voice_param(
                        param.name, param.id, value))
                if 'Write Temps' in param.name:
                    self.params.append(make_voice_param(
                        param.name, param.id, value))
                if 'Reload Cal' in param.name:
                    self.params.append(make_voice_param(
                        param.name, param.id, value))
            print("parameters: ")
            print(self.params)
        except Exception as ex:
            template = "Error: An exception of type '{0}' occurred:\n{1!r}"
            msg = template.format(type(ex).__name__, ex.args)
            print(msg)
            print(traceback.format_exc())
            self.controller.close()
            raise(ex)

    def getParam(self, find_name):
        return [obj for obj in self.params if obj.name == find_name][0]

    def setMainVca(self, run):
        param = self.getParam('Run VCA Cal:G')
        set_val = 0.0
        if run:
            set_val = 1.0
        self.controller.parameters.set_parameter_value(1, param.id, set_val)
    
    def setDcCal(self, run):
        param = self.getParam('Run DC Cal:G')
        set_val = 0.0
        if run:
            set_val = 1.0
        self.controller.parameters.set_parameter_value(1, param.id, set_val)
    
    def setDcOdCal(self, run):
        param = self.getParam('Run DC OD Cal:G')
        set_val = 0.0
        if run:
            set_val = 1.0
        self.controller.parameters.set_parameter_value(1, param.id, set_val)



    def setFilter(self, run):
        param = self.getParam('Run Filter Cal:G')
        print(self.params)
        print(param)
        set_val = 0.0
        if run:
            set_val = 1.0
        print("set filter....")
        print(param.id)
        print(set_val)
        self.controller.parameters.set_parameter_value(1, param.id, set_val)

    def setWriteTemp(self, run):
        param = self.getParam('Write Temps')
        set_val = 0.0
        if run:
            set_val = 1.0
        self.controller.parameters.set_parameter_value(1, param.id, set_val)

    def reloadCal(self, run):
        print("try to reload cal")
        param = self.getParam('Reload Cal:G')
        set_val = 0.0
        if run:
            set_val = 1.0
        self.controller.parameters.set_parameter_value(1, param.id, set_val)

    def LogCalInfo(self):
        self.setWriteTemp(True)
        time.sleep(1)
        self.setWriteTemp(False)
        file = "/udata/delia/tuning/cal_info.dat"
        array = np.fromfile(file, dtype="<f")
        print(array[0])
        return array

    def isTestDone(self):
        try:
            open(CAL_COMPLETE_FILE)
            return True
        except:
            return False

    def LogTemp(self):

        self.setWriteTemp(True)
        time_t = datetime.now() - self.start_time
        time_t = time_t.total_seconds()
        time.sleep(1)
        self.setWriteTemp(False)
        file = "/udata/delia/tuning/cal_info.dat"
        array = np.fromfile(file, dtype="<f")
        array = np.append(array, time_t)
        self.temp_data.append(array)
        


    def checkTuningDelta(self):
        array_mean = np.array(self.temp_data)
        array_mean = array_mean[:, 0::11]
        array_mean = np.mean(array_mean, 1)
        return array_mean[0] - array_mean[-1]

    def currentRateOfChange(self):
        array = np.array(self.temp_data)
        print("size", np.size(array))
        if(np.size(array) > 14):

            array_mean = array[:, 0::11]
            array_mean = np.mean(array_mean, 1)
            t_d = array[-1, 13] - array[-2, 13]
            y_d = array_mean[-1] - array_mean[-2]
            print("deltas ", t_d, y_d)
            return y_d/t_d
        return 1/500

def getSystemTemp():
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp = f.read()
        return int(temp) / 1000


#make sure that the disk is in RW mode so that python will run happily 
subprocess.run(
        ["elk_system_utils", "--remount-as-rw"])
deleteCalFile()
p = interface()
#now run the validation step 
print("run filter ")
p.setFilter(False)
time.sleep(.2)
p.setFilter(True)
test_done = False
while(not test_done):
    time.sleep(.2)
    test_done = p.isTestDone()
    
time.sleep(.2)
p.setFilter(False)
# run the filter cal script
print("run analysis")
time.sleep(.2)

ret = subprocess.call(["python3", "/home/root/delia/delia_vst.vst3/Contents/FilterTuningRoutine.py", "--validate"])
print("test complete " + str(ret))
subprocess.run(
    ["elk_system_utils", "--remount-as-ro"])
output_str = ""
with open ("/udata/delia/calibration/filter_cal_status.txt") as f:
    lines = f.readlines()
    pass_status = lines[0]
    print ("pass " + str(pass_status))
    errors  = lines[1].split(" ")
    while ("" in errors):
        errors.remove("")
    for v in range(5):
        if float(errors[v]) > THRESH:
            output_str = output_str + str(v) + ", "
    print(output_str)
    
with open("/tmp/filter_failed_voices.txt", "w") as f:
    f.write(output_str)
    
if(ret == 1):
    exit(1)
time.sleep(1)
print("done")