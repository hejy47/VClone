import Configuration
from BugCommit import Distribution, PatchCloneDetector

if __name__ == "__main__":

    print("===========================================")
    print("Statistics of diff hunk sizes of code changes")
    print("===========================================")
    Distribution.statistics(Configuration.PATCH_COMMITS_PATH, Configuration.DIFFENTRY_SIZE_PATH)

    print("\n\n\n===========================================")
    print("Detect the clone of code changes of patches")
    print("===========================================")
    PatchCloneDetector.detect(Configuration.PATCH_COMMITS_PATH, Configuration.PARSE_RESULTS_PATH)
