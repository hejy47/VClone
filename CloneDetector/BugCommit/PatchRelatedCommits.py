import os, shutil
from unidiff import PatchSet
from GitHelper.GitRepository import GitRepository
from DiffEntry.MessageFile import MessageFile
from utils import FileHelper

keywords = ["bug","error","fault","fix","patch","repair"]

def collectCommits(projectsPath, outputPath, urlPath):
    projects = os.listdir(projectsPath)
    FileHelper.deleteDirectory(outputPath)
    for project in projects:
        projectPath = os.path.join(projectsPath, project)
        if not os.path.isdir(projectPath): continue
        gitRepo = GitRepository(projectPath, revisedFilePath="", previousFilePath="")
        print("\nProject: ", project)
        gitRepo.open()
        commits = gitRepo.getAllCommits()
        print("All Commits: ", len(commits))
        keywordPatchCommits = gitRepo.filterByKeywords(commits, keywords)
        print("All collected patch-related Commits: ", len(keywordPatchCommits))

        patchCommitDiffentries = gitRepo.getCommitDiffEntries(keywordPatchCommits)
        diffEntriesPath = os.path.join(outputPath, "Keywords", project)
        commitMessagesPath = os.path.join(outputPath, "CommitMessage", project+"_Keywords.txt")
        gitRepo.createFilesForGumTree(diffEntriesPath, patchCommitDiffentries)
        gitRepo.outputCommitMessages(commitMessagesPath, keywordPatchCommits)

def filter(subjectsPath, outputPath):
    projects = os.listdir(subjectsPath)
    for project in projects:
        print("Filtering "+project)
        msgFiles = readMessageFiles(project, outputPath)
        total = len(msgFiles)
        parseEmpty = 0
        selectedCommits = []
        for msgFile in msgFiles:
            revFile = msgFile.getRevFile()
            prevFile = msgFile.getPrevFile()
            diffentryFile = msgFile.getDiffEntryFile()
            if not os.path.exists(revFile) or not os.path.exists(prevFile) or not os.path.exists(diffentryFile):
                total -= 1
                continue
            diffList = FileHelper.readFileToList(diffentryFile)
            diffStr = ''.join(diffList[2:])
            patch = PatchSet(diffStr)
            delLines, addLines = [], []
            for patchFile in patch:
                for patchHunk in patchFile:
                    for patchLine in patchHunk:
                        patchLineValue = patchLine.value.strip()
                        if patchLineValue != "" and not patchLineValue.startswith("//"):
                            if patchLine.is_removed:
                                delLines.append(patchLine.value)
                            elif patchLine.is_added:
                                addLines.append(patchLine.value)
            if delLines == [] and addLines == []:
                parseEmpty += 1
                total -= 1
                shutil.rmtree(os.path.dirname(prevFile))
                shutil.rmtree(os.path.dirname(revFile))
                os.remove(diffentryFile)
            else:
                selectedCommit = os.path.basename(revFile)[:17]
                if selectedCommit not in selectedCommits:
                    selectedCommits.append(selectedCommit)
        print("All MSGFiles:", total+parseEmpty)
        print("Parse Empty MSGFiles:", parseEmpty)
        print("Selected MSGFiles:", total)
        print("Selected Commits:", len(selectedCommits), "\n")

def readMessageFiles(projectName, path):
    msgFiles = []
    keywordPatchesFile = os.path.join(path, "Keywords", projectName)
    commitIds = []

    msgFiles = msgFiles + getMessageFiles(keywordPatchesFile, commitIds)
    return msgFiles

def getMessageFiles(projectPath, commitIds):
    msgFiles = []
    revFilesPath = os.path.join(projectPath, "revFiles")
    prevFilesPath = os.path.join(projectPath, "prevFiles")
    diffentryFilesPath = os.path.join(projectPath, "DiffEntries")
    if not os.path.exists(revFilesPath):
        return []
    revFilesSubPath = os.listdir(revFilesPath)
    for revFileSubPath in revFilesSubPath:
        prevFileSubPath = "prev_" + revFileSubPath
        diffentryFile = revFileSubPath + ".txt"
        revFilePath = os.path.join(revFilesPath, revFileSubPath, revFileSubPath)
        prevFilePath = os.path.join(prevFilesPath, prevFileSubPath, prevFileSubPath)
        for hdlType in [".v", ".vhd", ".vhdl", ".sv"]:
            if os.path.exists(revFilePath+hdlType) and os.path.exists(prevFilePath+hdlType):
                revFilePath = revFilePath+hdlType
                prevFilePath = prevFilePath+hdlType
                break
        msgFile = MessageFile(revFilePath, prevFilePath,\
            os.path.join(diffentryFilesPath, diffentryFile))
        msgFiles.append(msgFile)
        commitId = revFileSubPath[:8]
        if commitId not in commitIds: commitIds.append(commitId)
    return msgFiles