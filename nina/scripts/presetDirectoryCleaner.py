import hashlib
import os
import re
import time

start = time.time()

#calc hash of patch file
def check(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as fh:
        while True:
            data = fh.read(4096)
            if len(data) == 0:
                break
            else:
                h.update(data)
    return h.hexdigest()

working_dir  = "/udata/nina/presets/"

#cleanup the patch files
patches_dir = working_dir + "patches/"
blank_sha = "560fe0f119cf9cd778c85ecee0c72d4351ef56f7172bb94c1dfe3210d482aa5a"
source_dirs = os.listdir(patches_dir)
for r, d, f in os.walk(patches_dir):
    for file in f:
            
            #if file matches patch format
            if re.search("\d{3}_.*\.json$", file):
                
                #if file matches blank format
                if (re.search('\d{3}_BLANK\.json', file)):
                    blank_patch_path = (os.path.join(r, file))
                    hash = check(blank_patch_path)
                    
                    #delete if sha is correct
                    if(hash == blank_sha):
                        print("blank found at: " + blank_patch_path)
                        os.remove(os.path.join(r, file))
            #invalid files are deleted 
            else:
                print("bad file: " + file)
                os.remove(os.path.join(r, file))
            
#cleanup layers dir 
layers_dir = working_dir + "layers/"
layers_sha = "d1bfc28c5a1769a6a3d3d7e89b9c6a9ca11d31268b019bbc3a1ee16b2ea4fc3b"
source_dirs = os.listdir(layers_dir )
for r, d, f in os.walk(layers_dir):
    for file in f:
        
        #if file matches layer format
        if re.search("\d{3}_.*\.json$", file):
            
            #if file name matches old layers file 
            if (re.search('\d{3}_LAYERS\.json', file)):
                blank_layer_dir = (os.path.join(r, file))
                hash = check(blank_layer_dir)
                
                #if sha matches old layers file
                if(hash == layers_sha):
                    print("default layer found at: " + blank_layer_dir)
                    os.remove(os.path.join(r, file))
                    
        #invalid files are deleted
        else:
            print("bad file: " + file)
            os.remove(os.path.join(r, file))
            
print("checks complete")
end = time.time()
print(end - start)