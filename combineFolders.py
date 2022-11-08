import os, shutil
from imutils import paths
import numpy as np
import cv2
import os

def dhash(image, hashSize=8):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

curr = "0"
jordan = "1"
combiningFolders, renameFolder, removeDups = False, False, True
directory = "Data/"+jordan+"_images/"
if combiningFolders:
    for i in range(1, 7):
        dest = "Data/"+jordan+"_images/"
        directory = dest[:len(dest)-1]+","+str(i)+"/"
        for filename in os.listdir(directory):
            oldName, newName = directory+filename, directory+curr+".jpg"
            os.rename(oldName, newName)
            shutil.move(newName, dest)
            curr = str(int(curr)+1)
elif renameFolder:
    for filename in os.listdir(directory):
        oldName, newName = directory+filename, directory+curr+".jpg"
        os.rename(oldName, newName)
        curr = str(int(curr)+1)
elif removeDups:
    imagePaths = list(paths.list_images(directory))
    hashes = {}
    # loop over our image paths
    for imagePath in imagePaths:
        # load the input image and compute the hash
        image = cv2.imread(imagePath)
        if image is None:
            print(imagePath)
        else:
            h = dhash(image)
            # grab all image paths with that hash, add the current image
            # path to it, and store the list back in the hashes dictionary
            p = hashes.get(h, [])
            p.append(imagePath)
            hashes[h] = p
    count = 0
    for h in hashes:
        while len(hashes[h]) > 1:
            os.remove(hashes[h].pop(-1))
            count += 1
    print("removed", count, "duplciates")






