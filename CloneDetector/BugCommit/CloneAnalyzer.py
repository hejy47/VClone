import re
import os
import json
from collections import Counter

def formalizeString(codeString):
    codeStringList = codeString.replace(";", "").split("\n")
    for i, codeLine in enumerate(codeStringList):
        codeLineList = codeLine.split()
        codeStringList[i] = " ".join(codeLineList)
    retString = "\n".join(codeStringList)
    return retString
        

def cloneAnalysis(hunkInfo):
    donorCodes = []
    for _, addLine in hunkInfo["Diff Content"]["Add"]:
        donorCodes.append(formalizeString(addLine))

    pattern1 = re.compile("(.*?)@\d+:\d+@(.*)")
    result = re.search(pattern1, hunkInfo["Source Block"][0])
    buggyFile, statementType = result[1], result[2]
    clonesOfBugFix = []
    if donorCodes == []:
        return [], None, [], []
    else:
        clonesOfBugFixInLocal, clonesOfBugFixInGlobal = [], []
        for cloneInfo, cloneBlock in hunkInfo["Clone Blocks"]:
            pattern2 = re.compile("(.*?)@\d+:\d+")
            cloneFile = re.search(pattern2, cloneInfo)[1]
            cloneString = formalizeString(cloneBlock)
            for donorCode in donorCodes:
                if donorCode in cloneString:
                    clonesOfBugFixInGlobal.append([cloneInfo, cloneBlock])
                    if cloneFile == buggyFile:
                        clonesOfBugFixInLocal.append([cloneInfo, cloneBlock])
        return donorCodes, statementType, clonesOfBugFixInGlobal, clonesOfBugFixInLocal

def cloneStatistics(cloneDataPath):
    statementTypesInGlobal, statementTypesInLocal =[], []
    for repo in os.listdir(cloneDataPath):
        repoPath = os.path.join(cloneDataPath, repo)
        allHunks, cloneHunksInGlobal, cloneHunksInLocal = [], [], []
        for commit in os.listdir(repoPath):
            for hunk in os.listdir(os.path.join(repoPath, commit)):
                hunkPath = os.path.join(repoPath, commit, hunk)
                if not hunkPath.endswith(".json"): continue
                hunkInfo = ""
                with open(hunkPath, "r") as f:
                    hunkContent = f.read()
                    hunkInfo = json.loads(hunkContent)
                donorCodes, statementType, clonesOfBugFixInGlobal, clonesOfBugFixInLocal = cloneAnalysis(hunkInfo)
                if donorCodes != []:
                    allHunks.append(donorCodes)
                    if clonesOfBugFixInGlobal != []:
                        cloneHunksInGlobal.append((donorCodes, clonesOfBugFixInGlobal))
                        statementTypesInGlobal.append(statementType)
                    if clonesOfBugFixInLocal != []:
                        cloneHunksInLocal.append((donorCodes, clonesOfBugFixInLocal))
                        statementTypesInLocal.append(statementType)
        print("\n\nResult\n========================")
        print("{}\n===========".format(repo))
        print("all Hunks: {}".format(len(allHunks)))
        print("clone of bug fix in global: {}".format(len(cloneHunksInGlobal)))
        print("clone of bug fix in lobal: {}\n\n".format(len(cloneHunksInLocal)))
    
    typesStatisticGlobal, typesStatisticLocal = Counter(statementTypesInGlobal), Counter(statementTypesInLocal)
    print("statement types distribution in global:\n", typesStatisticGlobal)
    print("statement types distribution in local:\n", typesStatisticLocal)
