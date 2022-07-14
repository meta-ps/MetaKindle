import os
import shutil
from config.settings import BASE_DIR


path1= BASE_DIR+"/FilDrop/__pycache__"
path2= BASE_DIR+"/FilDrop/migrations"
path3=BASE_DIR+'/db.sqlite3'

try:
    shutil.rmtree(path1)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))

try:
    shutil.rmtree(path2)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))

try:
    shutil.rmtree(path3)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))
