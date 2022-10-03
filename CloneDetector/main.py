import Configuration
from BugCommit import Distribution
from BugCommit import PatchRelatedCommits

if __name__ == "__main__":
    print("===========================================")
    print("Statistics of project LOC")
    print("===========================================")
    Distribution.countLOC(Configuration.SUBJECTS_PATH)

    print("===========================================")
    print("Collect bug fixing commits")
    print("===========================================")
    PatchRelatedCommits.collectCommits(Configuration.SUBJECTS_PATH, Configuration.PATCH_COMMITS_PATH, Configuration.BUG_REPORTS_PATH)

    print("\n\n\n===========================================")
    print("Filter out non-Verilog code changes and unparseable code")
    print("===========================================")
    PatchRelatedCommits.filter(Configuration.SUBJECTS_PATH, Configuration.PATCH_COMMITS_PATH)
