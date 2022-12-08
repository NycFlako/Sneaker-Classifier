import os, shutil, csv, cv2, random
from imutils import paths
from PIL import Image
import numpy as np

"""
Flags used to remove duplicates, rename folders and combining folders when
creating the dataset.
"""
curr, jordan = "0", "1"
combiningFolders, renameFolder, removeDups = False, False, False
directory = "Data/"+jordan+"_images/"

"""
Converts png images to jpg
"""
def convert2jpg(path):
    image = cv2.imread(path)
    cv2.imwrite(path[:-3]+"jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    os.remove(path)

"""
This function will go through the dataset and find the mean dimension across it.
"""
def findScale():
    path = "Data/"
    width, height, count = 0, 0, 0
    for filename in os.listdir(path):
        if ".DS_Store" not in filename:
            for img in os.listdir(path+filename):
                if ".jpg" in img:
                    image = cv2.imread(path+filename+"/"+img)
                    size = image.shape
                    width += size[1]
                    height += size[0]
                    count += 1
    return (height//count, width//count)

'''
Takes in a dimension and 2 optional parameters: scale and check
By default the function will resize all of the images to the dimension 
specified by dim. 

When scale is not None it should be set to a percent between 0 and 1 exclusive
to which the images will be scaled. 

When check is set to True it will check that all images in the dataset are
the same as dim.
'''
def resizeImages(dim, scale = None, check = False):
    path = "Data/"
    for filename in os.listdir(path):
        if ".DS_Store" not in filename:
            for img in os.listdir(path+filename):
                if ".jpg" in img:
                    imgPath = path+filename+"/"+img
                    image = cv2.imread(imgPath)
                    if check == True:
                        imgDim = (image.shape[0], image.shape[1])
                        if imgDim != dim:
                            print(imgDim, dim, imgPath)
                    else:
                        if scale != None:
                            height, width = image.shape[0], image.shape[1]
                            dim = (int(height*scale), int(width*scale))
                        resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
                        try:
                            cv2.imwrite(imgPath, resized) 
                        except:
                            print("Error writing:", imgPath)

"""
Hashing functions to remove any duplicates downloads that may have occurred.
"""
def dhash(image, hashSize=8):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

"""
Combine the different folders from the current jordan class onto one folder
"""
def combineFolders(jordan, curr):
    for i in range(1, 7):
        dest = "Data/"+jordan+"_images/"
        directory = dest[:len(dest)-1]+","+str(i)+"/"
        for filename in os.listdir(directory):
            oldName, newName = directory+filename, directory+curr+".jpg"
            os.rename(oldName, newName)
            shutil.move(newName, dest)
            curr = str(int(curr)+1)

"""
Renames the folder for the current jordan class
"""
def renameFolder(directory, curr):
    for filename in os.listdir(directory):
        oldName, newName = directory+filename, directory+curr+".jpg"
        os.rename(oldName, newName)
        curr = str(int(curr)+1)

"""
Removes all of the duplicates images that could be found in the directory
through hashing the pixel values and distribution.
"""
def removeDups(directory):
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
    print("removed", count, "duplicates")


def resizeData():
    height, width = findScale()
    print("Mean Dimensions:", height, width)

    percent = 100/max(height, width)
    print("Scaled dimensions", int(height*percent), int(width*percent))
    resizeImages((int(width*percent), int(height*percent)))

    print("Checking dimensions...", end="")
    resizeImages((int(height*percent), int(width*percent)), check = True)
    print("Done checking!")

def renameData(path):
    for filename in os.listdir(path):
        if ".DS_Store" not in filename:
            print(filename)
            label = filename[0]
            for img in os.listdir(path+filename):
                index = img.find(".")
                newImg = img[:index]+"_"+label+".jpg"
                oldName = path+filename+"/"+img
                newName = path+filename+"/"+newImg
                os.rename(oldName, newName)

def createRow(image, label):
    L = [image] + [0]*5
    L[label] = 1
    return L

def createCSV(path):
    kinds = ["train", "test"]
    for kind in kinds:
        with open(kind+'.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['img', 'Jordan 1', 
                                'Jordan 2', 'Jordan 3', 'Jordan 4', 'Jordan 5'])
            for img in os.listdir(path+"color/"+kind+"/"):
                if ".DS_Store" not in img:
                    index = img.find(".")
                    label = int(img[index-1])
                    newRow = createRow(img, label)
                    filewriter.writerow(newRow)
    
createCSV("Data/")
def moveData(path):
    for filename in os.listdir(path):
        if ".DS_Store" not in filename:
            for img in os.listdir(path+filename):
                imgPath = path+filename+"/"+img
                shutil.move(imgPath, path)

def convertGray(path):
    for img in os.listdir(path):
        if ".DS_Store" not in img:
            img_rgb = Image.open(path+img)
            img_gray = img_rgb.convert('L')
            img_gray.save("grayscale/"+"gray_"+img)

def train_test_split(path):
    toTest, total = list(), 150
    map = {1: [], 2: [], 3: [], 4: [], 5: []}

    # Creating map for each of the classes
    for img in os.listdir(path+"grayscale/"):
        if "." in img and img != ".DS_Store":
            label = int(img[img.index(".")-1])
            map[label].append(img)

    # Getting the 30% to test on
    for label in map:
        for _ in range(int(len(map[label])*.3)):
            randomImage = random.choice(map[label])
            map[label].remove(randomImage)
            toTest.append(randomImage)
    
    # Moving the testing data to its own directory
    for filename in os.listdir(path):
        if ".DS_Store" != filename:
            for file in toTest:
                if filename == "color":
                    oldPath = path+filename+"/"+file[5:]
                    newPath = path+filename+"/test/"+file[5:]
                else:
                    oldPath = path+filename+"/"+file
                    newPath = path+filename+"/test/"+file[5:]
            shutil.move(oldPath, newPath)


def rescaleData(path, scale, fixedDim = None):
    for filename in os.listdir(path):
        if ".DS_Store" not in filename:
            for kind in os.listdir(path+filename):
                if kind != ".DS_Store":
                    for img in os.listdir(path+filename+"/"+kind):
                        if ".DS_Store" != img:
                            imgPath = path+filename+"/"+kind+"/"+img
                            image = cv2.imread(imgPath)
                            height, width = image.shape[0], image.shape[1]
                            dim = (int(width*scale), int(height*scale))
                            if fixedDim != None:
                                resized = cv2.resize(image, fixedDim, interpolation = cv2.INTER_AREA)
                            else:
                                resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
                            try:
                                cv2.imwrite(imgPath, resized) 
                            except:
                                print("Error writing:", imgPath)

def renameFiles(path):
    for filename in os.listdir(path):
        if filename != ".DS_Store":
            os.rename(path+filename, path+filename[5:])

def makeDataClass():
    path = "Data/"
    for i in range(1, 6):
        os.makedirs(path+str(i)+"_images")
    for kind in ["train", "test"]:
        for file in os.listdir(path+"color/"+kind):
            if file != ".DS_Store":
                folder = file[file.index('.')-1]+"_images"
                oldPath = path+"color/"+kind+"/"+file
                newPath = path+folder+"/"+file
                shutil.copyfile(oldPath, newPath)

def resizeTest(path):
    toMove = {1: [], 2: [], 3: [], 4: [], 5: []}
    total = list()
    for file in os.listdir(path+"color/test/"):
        if file != ".DS_Store":
            label = int(file[file.index(".")-1])
            toMove[label].append(file)

    for label in toMove:
        for _ in range(int(len(toMove[label])*(2/3))):
            randomImage = random.choice(toMove[label])
            toMove[label].remove(randomImage)
            total.append(randomImage)

    for img in total:
        for kind in ["color/", "grayscale/"]:
            oldPath = path+kind+"test/"+img
            newPath = path+kind+"train/"+img
            shutil.move(oldPath, newPath)