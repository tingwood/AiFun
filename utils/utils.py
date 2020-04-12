import os
import time
import uuid
#from path import Path

#dir = r"d:/demo"
#d = Path(dir)

# Change the DAYS to your liking
#DAYS = 6
# Replace DIRECTORY with your required directory
#time_in_secs = time.time() - (DAYS * 24 * 60 * 60)

#for f in d.walk():
#    if f.isfile():  # and f.mtime <= time_in_secs
#        f.remove()
#        pass
#    elif f.isdir():
#        try:
#            f.remove()
#        except Exception as e:
#            print(e)
#    else:
#        pass

def mkdirs(dir):
    folder = os.path.exists(dir)
    if not folder:
        os.makedirs(dir)

def genUuid():
    id = uuid.uuid1()
    return str(id).replace("-", "")
