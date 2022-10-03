import os
import shutil

from git import exc

def getAllFiles(filePath):
    if not os.path.exists(filePath):
        return None
    fileList = []
    if os.path.isfile(filePath) and (filePath.endswith(".v") or filePath.endswith(".vhd") or filePath.endswith(".vhdl") or filePath.endswith(".sv")):
        fileList.append(filePath)
    if os.path.isdir(filePath) and not os.path.islink(filePath):
        files = os.listdir(filePath)
        for f in files:
            fPath = os.path.join(filePath, f)
            fl = getAllFiles(fPath)
            if fl != None: fileList.extend(fl)
    return fileList

def creatCSV(fileName, fileContent):
    parentDirectory = os.path.dirname(fileName)
    if not os.path.exists(parentDirectory):
        os.makedirs(parentDirectory)
    fileContent.to_csv(fileName)

def creatFile(fileName, fileContent):
    parentDirectory = os.path.dirname(fileName)
    if not os.path.exists(parentDirectory):
        os.makedirs(parentDirectory)
    with open(fileName, 'w') as f:
        try:
            f.write(fileContent)
        except Exception as e:
            print(e)
            print("write error")

def deleteFile(filePath):
    if os.path.exists(filePath) and os.path.isfile(filePath):
        os.remove(filePath)

def deleteDirectory(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)

def deleteALLSubDirectory(dir):
    if os.path.exists(dir):
        for subDir in os.listdir(dir):
            subPath = os.path.join(dir, subDir)
            if os.path.isfile(subPath):
                deleteFile(subPath)
            elif os.path.isdir(subPath):
                deleteDirectory(subPath)

def copyFile(srcFilePath, dstFilePath):
    if os.path.exists(srcFilePath) and os.path.isfile(srcFilePath):
        shutil.copyfile(srcFilePath, dstFilePath)

def copyDirectory(srcDir, dstDir):
    if os.path.isdir(dstDir):
        deleteDirectory(dstDir)
    if os.path.exists(srcDir) and os.path.isdir(srcDir):
        shutil.copytree(srcDir, dstDir)

def readFileToStr(srcPath):
    with open(srcPath, 'r') as f:
        ret = f.read()
        return ret

def readFileToList(srcPath):
    with open(srcPath, 'r') as f:
        ret = f.readlines()
        return ret

def writeStrToFile(content, dstPath):
    with open(dstPath, 'w') as wf:
        wf.write(content)