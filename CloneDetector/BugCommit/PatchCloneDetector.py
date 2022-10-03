import os, re, json
import git
from unidiff import PatchSet
import Configuration
from BugCommit import CloneAnalyzer
from DiffEntry.MessageFile import MessageFile
from utils import FileHelper, CmdHelper

def readMessageFiles(pathCommitsPath, dataType):
    msgFiles = {}
    projects = os.listdir(os.path.join(pathCommitsPath, dataType))
    for project in projects:
        repoMsgFiles = []
        projectPath = os.path.join(pathCommitsPath, dataType, project)
        if os.path.isdir(projectPath):
            revFilesPath = os.path.join(projectPath, "revFiles")
            prevFilesPath = os.path.join(projectPath, "prevFiles")
            diffentryFilesPath = os.path.join(projectPath, "DiffEntries")
            revFilesSubPath = os.listdir(revFilesPath)
            for revFileSubPath in revFilesSubPath:
                if os.path.isdir(os.path.join(revFilesPath, revFileSubPath)):
                    prevFileSubPath = "prev_" + revFileSubPath
                    diffentryFile = revFileSubPath + ".txt"
                    revFilePath = os.path.join(revFilesPath, revFileSubPath, revFileSubPath)
                    prevFilePath = os.path.join(prevFilesPath, prevFileSubPath, prevFileSubPath)
                    for hdlType in [".v", ".vhd", ".vhdl", ".sv"]:
                        if os.path.exists(revFilePath+hdlType) and os.path.exists(prevFilePath+hdlType):
                            revFilePath = revFilePath+hdlType
                            prevFilePath = prevFilePath+hdlType
                            break
                    msgFile = MessageFile(revFilePath, prevFilePath, os.path.join(diffentryFilesPath, diffentryFile))
                    repoMsgFiles.append(msgFile)
        msgFiles[project] = repoMsgFiles
    return msgFiles

def readStatsFiles(statsPath):
    statsDict = {}
    for statsFile in os.listdir(statsPath):
        statsList = FileHelper.readFileToList(os.path.join(statsPath, statsFile))
        currentFile = ""
        for statsLine in statsList:
            if statsLine.startswith("f"):
                fStats = statsLine.replace("\n", "").split(",")
                currentFile = fStats[2][1:-1].replace("data/", "")
            elif statsLine.startswith("b"):
                bStats = statsLine.replace("\n", "").split(",")
                bId = "{},{}".format(bStats[0][1:], bStats[1])
                # bInfo = "{} ({},{})".format(currentFile, bStats[-2], bStats[-1])
                bInfo = "{} ({},{}) {} ({},{})".format(currentFile, bStats[-5], bStats[-4], bStats[-3], bStats[-2], bStats[-1])
                statsDict[bId] = bInfo
    return statsDict

def backupCloneFiles(statsPath, blocksPath, resultsPath, targetPath):
    # backup stats files
    FileHelper.copyDirectory(statsPath, os.path.join(targetPath, os.path.basename(statsPath)))

    # backup blocksPath
    FileHelper.copyFile(blocksPath, os.path.join(targetPath, os.path.basename(blocksPath)))

    # backup resultsPath
    FileHelper.copyFile(resultsPath, os.path.join(targetPath, os.path.basename(resultsPath)))

def detect(patchPath, outputPath):
    FileHelper.deleteALLSubDirectory(Configuration.CLONE_PATH)
    msgFiles = readMessageFiles(patchPath, "Keywords")
    for repoName, repoMsgFiles in msgFiles.items():
        # if repoName not in ["picorv32", "e200_opensource", "wujian100_open", "hw", "verilog-ethernet", "hdl", "amiga2000-gfxcard", "zipcpu", "oh", "serv", "miaow"]: continue
        print("Detecting {}...".format(repoName))
        for repoMsgFile in repoMsgFiles:
            revFile = repoMsgFile.getRevFile()
            prevFile = repoMsgFile.getPrevFile()
            diffentryFile = repoMsgFile.getDiffEntryFile()

            diffList = FileHelper.readFileToList(diffentryFile)
            diffStr = ''.join(diffList[2:])
            patch = PatchSet(diffStr)
            delLines, addLines = [], []
            for patchFile in patch:
                for patchHunk in patchFile:
                    buggyLocation = patchHunk.source_start
                    for patchLine in patchHunk:
                        patchLineValue = patchLine.value.strip()
                        if patchLineValue != "" and not patchLineValue.startswith("//"):
                            if patchLine.is_removed:
                                delLines.append((patchFile.source_file.replace("a/", ""), patchLine.source_line_no, patchLine.value))
                                buggyLocation = patchLine.source_line_no
                            elif patchLine.is_added:
                                if patchFile.source_file != None:
                                    addLines.append((patchFile.source_file.replace("a/", ""), buggyLocation, patchLine.value))
                            else:
                                buggyLocation = patchLine.source_line_no
            
            prevFilePathList = prevFile.split('/')
            prevFileName = prevFilePathList[-1][5:]
            repoName = prevFilePathList[-4]
            projectPath = os.path.join(Configuration.SUBJECTS_PATH, repoName)
            prevCommitId = prevFileName[9:17]
            prevFilePath = prevFileName[18:].replace('#', '/')
            repo = git.Repo(projectPath)

            # tokenize the repository
            FileHelper.deleteALLSubDirectory(Configuration.TOKENIZERS_DATA_PATH)
            prevRepoPath = os.path.abspath(os.path.join(Configuration.TOKENIZERS_DATA_PATH, repoName))

            repo.git.checkout(prevCommitId, "--force")
            repo.clone(prevRepoPath)
            repo.git.checkout(".", "--force")

            allDirs = []
            for home, dirs, files in os.walk(os.path.join(Configuration.TOKENIZERS_DATA_PATH, repoName)):
                for dir in dirs:
                    dirPath = os.path.join(home, dir)
                    if ".git" in dirPath:
                        continue
                    allDirs.append(dirPath.replace(Configuration.TOKENIZERS_PATH, ""))
            FileHelper.writeStrToFile("{}\n".format("\n".join(allDirs)), Configuration.TOKENIZERS_CONF_PATH)

            # backup path
            diffBaseName = os.path.basename(diffentryFile)
            backupPath = os.path.join(Configuration.CLONE_BACKUP_PATH, repoName, diffBaseName[:17])

            if not os.path.exists(backupPath):
                cleanCmd = "sh cleanup.sh"
                CmdHelper.runCmd(cleanCmd, cwd=Configuration.TOKENIZERS_PATH)
                tokenizeCmd = "python tokenizer.py folderblocks"
                CmdHelper.runCmd(tokenizeCmd, cwd=Configuration.TOKENIZERS_PATH)
                mergeTokensCmd = "cat blocks_tokens/* > blocks.file"
                CmdHelper.runCmd(mergeTokensCmd, cwd=Configuration.TOKENIZERS_PATH)

                if os.path.exists(os.path.join(Configuration.TOKENIZERS_PATH, "blocks.file")):
                    FileHelper.copyFile(os.path.join(Configuration.TOKENIZERS_PATH, "blocks.file"), os.path.join(Configuration.DETECTOR_INPUT_PATH, "blocks.file"))
                detectCmd = "python controller.py"
                CmdHelper.runCmd(detectCmd, cwd=Configuration.DETECTOR_PATH)
                mergeResultsCmd = "cat NODE_*/output7.0/query_* > results.pairs"
                CmdHelper.runCmd(mergeResultsCmd, cwd=Configuration.DETECTOR_PATH)

                # backup blocks.file and results.pairs
                os.makedirs(backupPath)
                backupCloneFiles(Configuration.TOKENIZERS_STATS_PATH, os.path.join(Configuration.TOKENIZERS_PATH, "blocks.file"), Configuration.DETECTOR_RESULT_PATH, backupPath)
            

            # get related id of buggy code snippet
            statsDict = readStatsFiles(os.path.join(backupPath, os.path.basename(Configuration.TOKENIZERS_STATS_PATH)))
            relatedStatsIds = {}
            for statsId, statsInfo in statsDict.items():
                # pattern = "(.*?) \((\d+),(\d+)\)"
                pattern = "(.*?) \((\d+),(\d+)\) (.*?) \((\d+),(\d+)\)"
                statsInfoList = re.findall(pattern, statsInfo)[0]
                for delLine in delLines:
                    # if delLine[0] in statsInfoList[0] and int(delLine[1]) >= int(statsInfoList[1]) and int(delLine[1]) <= int(statsInfoList[2]):
                    if delLine[0] in statsInfoList[0] and int(delLine[1]) >= int(statsInfoList[4]) and int(delLine[1]) <= int(statsInfoList[5]):
                        if statsId not in relatedStatsIds: relatedStatsIds[statsId] = [[],[]]
                        relatedStatsIds[statsId][0].append((delLine[1], delLine[2]))
                for addLine in addLines:
                    # if addLine[0] in statsInfoList[0] and int(addLine[1]) >= int(statsInfoList[1]) and int(addLine[1]) <= int(statsInfoList[2]):
                    if addLine[0] in statsInfoList[0] and int(addLine[1]) >= int(statsInfoList[4]) and int(addLine[1]) <= int(statsInfoList[5]):
                        if statsId not in relatedStatsIds: relatedStatsIds[statsId] = [[],[]]
                        relatedStatsIds[statsId][1].append((addLine[1], addLine[2]))

            # get paris results
            targetPairs = {}
            resultPairs = FileHelper.readFileToList(os.path.join(backupPath, os.path.basename(Configuration.DETECTOR_RESULT_PATH)))
            for resultPair in resultPairs:
                rPair = resultPair.replace("\n", "")
                for relatedStatsId in relatedStatsIds.keys():
                    if relatedStatsId in rPair:
                        targetPair = rPair.replace(relatedStatsId, "")
                        if targetPair.startswith(","):
                            targetPair = targetPair[1:]
                        elif targetPair.endswith(","):
                            targetPair = targetPair[:-1]
                        if relatedStatsId not in targetPairs:
                            targetPairs[relatedStatsId] = set()
                        targetPairs[relatedStatsId].add(targetPair)
            
            # get the src and clone code fragments
            cloneInfoId = 1
            for srcStatsId, diffBlocks in relatedStatsIds.items():
                srcStatsInfo = statsDict[srcStatsId]
                pattern = "(.*?) \((\d+),(\d+)\) (.*?) \((\d+),(\d+)\)"
                srcStatsInfoList = re.findall(pattern, srcStatsInfo)[0]
                startLineNo, endLineNo = int(srcStatsInfoList[1]), int(srcStatsInfoList[2])
                srcFileContent = FileHelper.readFileToList(os.path.join(Configuration.TOKENIZERS_DATA_PATH, srcStatsInfoList[0]))
                srcBlock = "".join(srcFileContent[startLineNo-1:endLineNo])
                if startLineNo == 0:
                    srcBlock = "".join(srcFileContent[startLineNo:endLineNo])
                cloneBlocks = []
                if srcStatsId in targetPairs:
                    cloneStatsIds = targetPairs[srcStatsId]
                    for cloneStatsId in cloneStatsIds:
                        cloneStatsInfo = statsDict[cloneStatsId]
                        pattern = "(.*?) \((\d+),(\d+)\) (.*?) \((\d+),(\d+)\)"
                        cloneStatsInfoList = re.findall(pattern, cloneStatsInfo)[0]
                        startLineNo, endLineNo = int(cloneStatsInfoList[1]), int(cloneStatsInfoList[2])
                        cloneFileContent = FileHelper.readFileToList(os.path.join(Configuration.TOKENIZERS_DATA_PATH, cloneStatsInfoList[0]))
                        cloneBlock = "".join(cloneFileContent[startLineNo-1:endLineNo])
                        if startLineNo == 0:
                            cloneBlock = "".join(cloneFileContent[startLineNo:endLineNo])
                        cloneBlocks.append(("{}@{}:{}".format(cloneStatsInfoList[0], cloneStatsInfoList[1], cloneStatsInfoList[2]), cloneBlock))
                
                cloneInfo = {
                    "Source Block": ("{}@{}:{}@{}".format(srcStatsInfoList[0], srcStatsInfoList[1], srcStatsInfoList[2], srcStatsInfoList[3]), srcBlock),
                    "Clone Blocks": cloneBlocks,
                    "Diff Content": {
                        "Delete": diffBlocks[0],
                        "Add": diffBlocks[1]
                        }
                    }
                
                # show the clone info in txt
                cloneInfoTxt = "Source Block: {}@{}:{}@{}\n".format(srcStatsInfoList[0], srcStatsInfoList[1], srcStatsInfoList[2], srcStatsInfoList[3])
                cloneInfoTxt += srcBlock + "\n"
                cloneInfoTxt += "Diff Content:\n"
                for delL in diffBlocks[0]:
                    cloneInfoTxt += "- {} {}".format(delL[0], delL[1])
                for addL in diffBlocks[1]:
                    cloneInfoTxt += "+ {} {}".format(addL[0], addL[1])
                cloneInfoTxt += "\nClone Blocks:\n"
                for i, cloneBlock in enumerate(cloneBlocks):
                    cloneInfoTxt += "Clone Blocks {}:\n".format(i+1)
                    cloneInfoTxt += cloneBlock[0] + "\n" + cloneBlock[1] + "\n"

                diffBaseName = os.path.basename(diffentryFile)
                cloneInfoPath = os.path.join(Configuration.CLONE_PATH, repoName, diffBaseName[:17], diffBaseName.replace(".txt", "_{}.json".format(cloneInfoId)))
                cloneInfoTxtPath = cloneInfoPath.replace(".json", ".txt")
                cloneInfoId += 1

                # save the clone info
                if not os.path.exists(os.path.dirname(cloneInfoPath)):
                    os.makedirs(os.path.dirname(cloneInfoPath))
                FileHelper.writeStrToFile(json.dumps(cloneInfo), cloneInfoPath)
                FileHelper.writeStrToFile(cloneInfoTxt, cloneInfoTxtPath)
    
    # statistics
    CloneAnalyzer.cloneStatistics(Configuration.CLONE_PATH)