import os
import pandas as pd
from DiffEntry.DiffEntryHunk import DiffEntryHunk
from utils import FileHelper

def readDiffEntryHunks(diffentryFile):
    diffEntryHunks = []
    with open(diffentryFile, 'r') as f:
        content = f.readlines()
        if len(content) == 0:
            return []
        commitId = content[0]
        commitMessage = content[1]
        diffFile = content[4:6]
        diffContent = content[6:]
        hunkContents = []
        hunkContent = []
        for line in diffContent:
            if line.startswith("@@") and len(hunkContent) != 0:
                hunkContents.append(hunkContent)
                hunkContent = [line]
            else: hunkContent.append(line)
        if len(hunkContent) != 0: hunkContents.append(hunkContent)
        for hunkContent in hunkContents:
            line = hunkContent[0]
            buggyStartLine, buggyRange, buggyHunkSize = 0, 0, 0
            fixedStartLine, fixedRange, fixedHunkSize = 0, 0, 0
            if line.startswith("@@"):
                plusIndex = line.find("+")
                lineNum = line[4:plusIndex-1]
                nums = lineNum.split(",")
                buggyStartLine = eval(nums[0])
                if (len(nums) == 2):
                    buggyRange = eval(nums[1])
                
                lastIndex = line.rfind("@@")
                lineNum2 = line[plusIndex:lastIndex-1]
                nums2 = lineNum2.split(",")
                fixedStartLine = eval(nums2[0])
                if (len(nums2) == 2):
                    fixedRange = eval(nums2[1])
            for l in hunkContent[1:]:
                if l.startswith("-"):
                    buggyHunkSize += 1
                elif l.startswith("+"):
                    fixedHunkSize += 1
                
            diffEntryHunk = DiffEntryHunk(commitId, commitMessage, diffFile, buggyStartLine, fixedStartLine, buggyRange, fixedRange)
            diffEntryHunk.setDiffEntryHunkContent("".join(hunkContent))
            diffEntryHunk.setBuggyHunkSize(buggyHunkSize)
            diffEntryHunk.setFixedHunkSize(fixedHunkSize)
            diffEntryHunks.append(diffEntryHunk)
    return diffEntryHunks

def countLOC(subjectsPath):
    projects = os.listdir(subjectsPath)
    for project in projects:
        projectPath = os.path.join(subjectsPath, project)
        if os.path.isdir(projectPath):
            allVerilogFiles = FileHelper.getAllFiles(projectPath)
            
            fileCounter, locCounter = 0, 0
            for verilogFile in allVerilogFiles:
                fileLowerName = verilogFile.lower()
                if "tb" in fileLowerName or "test" in fileLowerName or "testbench" in fileLowerName:
                    continue
                reader = open(verilogFile, 'r', errors="ignore")
                fileContent = reader.readlines()
                fileCounter += 1
                locCounter += len(fileContent)
            print(project, " Source File Num: ", fileCounter, " LOC: ", locCounter)

def statistics(inputPath, outputPath):
    dataTypes = os.listdir(inputPath)
    diffentryRangeName = ["Hunk_Type", "Size"]
    diffentryRange = []
    buggyHunkSizes = []
    fixedHunkSizes = []
    for dataType in dataTypes:
        if os.path.isdir(os.path.join(inputPath, dataType)):
            projects = os.listdir(os.path.join(inputPath, dataType))
            for project in projects:
                projectPath = os.path.join(inputPath, dataType, project)
                if os.path.isdir(projectPath):
                    diffentryFiles = os.listdir(os.path.join(projectPath, "DiffEntries"))
                    for diffentryFile in diffentryFiles:
                        diffentryFilePath = os.path.join(projectPath, "DiffEntries", diffentryFile)
                        if os.path.isfile(diffentryFilePath) and diffentryFilePath.endswith(".txt"):
                            diffentryHunks = readDiffEntryHunks(diffentryFilePath)
                            for hunk in diffentryHunks:
                                bugRange = hunk.getBugRange()
                                fixRange = hunk.getFixRange()
                                buggyHunkSizes.append(bugRange)
                                fixedHunkSizes.append(fixRange)
                                diffentryRange.append(["Buggy_Hunk", str(bugRange)])
                                diffentryRange.append(["Fixed_Hunk", str(fixRange)])
    diffEntryRange = pd.DataFrame(columns=diffentryRangeName, data=diffentryRange)
    FileHelper.creatCSV(os.path.join(outputPath, "DiffEntryRange.csv"), diffEntryRange)
    summary(buggyHunkSizes, "buggy hunk")
    summary(fixedHunkSizes, "fixed hunk")

def summary(sizes, type):
    sizes.sort()

    size = len(sizes)
    firstQuaterIndex = size // 4
    firstQuater = sizes[firstQuaterIndex]
    thirdQuaterIndex = size * 3 // 4
    thirdQuater = sizes[thirdQuaterIndex]
    upperWhisker = thirdQuater + (thirdQuater - firstQuater) * 3 // 2
    maxSize = sizes[-1]
    upperWhisker = maxSize if upperWhisker > maxSize else upperWhisker

    print("Summary", type, "sizes:")
    print("Min:", sizes[0])
    print("First quartile:", firstQuater)
    print("Mean:", sum(sizes) / size)
    print("Third quartile:", thirdQuater)
    print("Upper whisker:", upperWhisker)
    print("Max:", maxSize)
