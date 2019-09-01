import os

def listFolder():
    list =  [x[0] for x in os.walk('/mnt/INTERNAL')]
    retlist = []
    for folder in list:
        if '.@__thumb' not in folder:
            retlist.append(folder)

    return retlist

