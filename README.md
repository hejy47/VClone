# 1. VClone

<!-- title: VClone --> 

****VClone**** is a tool of collecting patch-related commits and detecting the clones of real bug fixes in Verilog HDL.
It can automatically collects bug fixing commits from HDL repositories, and detects the clone pairs of buggy snippets by leveraging hdlConvertor and SourcecerCC. Furthermore, it can analyze the code clones of bug fix that contain donor code for  automated program repair.

- [1. VClone](#1-vclone)
  - [1.1. Introduction](#11-introduction)
  - [1.2. Environment setup](#12-environment-setup)
    - [1.2.1. Requirements](#121-requirements)
    - [1.2.2. Execution](#122-execution)
      - [1.2.2.1 Collecting Verilog projects from GitHub to create the subjects:](#1221-collecting-verilog-projects-from-github-to-create-the-subjects)
      - [1.2.2.2 Collecting patch-related commits, detecting and analyzing code clones of bug fixes](#1222-collecting-patch-related-commits-detecting-and-analyzing-code-clones-of-bug-fixes)

## 1.1. Introduction

Few studies focus on bug fixes of HDLs, which hinders the proposal of automated program repair (APR) techniques targeting HDLs. An important problem is that there is no validation of the redundancy assumption for APR that donor code for bug fixes can obtained from existing code.

With such motivation, we propose an automated technique named VClone for **code clone detection of bug fixes in Verilog**. We run VClone to validate the redundancy assumption based on the bug fixing commits in the open-source Verilog repositories. Furthermore, we provide a way to find donor codes.

## 1.2. Environment setup
### 1.2.1. Requirements

+ Ubuntu 20.04
+ Python >= 3.8.0
+ [hdlConvertor](https://github.com/Nic30/hdlConvertor)
+ [SourcererCC](https://github.com/Mondego/SourcererCC)

### 1.2.2. Execution

#### 1.2.2.1 Collecting Verilog projects from GitHub to create the subjects:

****Repositories in Verilog****

* [picorv32](https://github.com/cliffordwolf/picorv32.git)
* [e200_opensource](https://github.com/SI-RISCV/e200_opensource.git)
* [wujian100](https://github.com/T-head-Semi/wujian100_open.git)
* [hw](https://github.com/nvdla/hw.git)
* [verilog-ethernet](https://github.com/alexforencich/verilog-ethernet.git)
* [hdl](https://github.com/analogdevicesinc/hdl.git)
* [amiga2000-gfxcard](https://github.com/mntmn/amiga2000-gfxcard.git)
* [corundum](https://github.com/corundum/corundum.git)
* [zipcpu](https://github.com/ZipCPU/zipcpu.git)
* [oh](https://github.com/aolofsson/oh.git)
* [serv](https://github.com/olofk/serv.git)
* [miaow](https://github.com/VerticalResearchGroup/miaow.git)

****commads****

* `./collect_subjects.sh` After runing it, there are a total of 12 repositories written in Verilog HDL cloned into `subjects`.

#### 1.2.2.2 Collecting patch-related commits, detecting and analyzing code clones of bug fixes

* `./run.sh`

- If it executes successfully
  - The **first step** makes statistics of project LOC, which show the code line numbers of all projects respectively.
  - The **second step** collects bug-fix-related commits with bug-related keywords from project repositories.
It also will fileter out changes of test code. Its output consists of three kinds of files. The results in Verilog are stored in `data` respectively.
      - **Buggy version** of a HDL code file containing a bug, stored in the directory "`data/PatchCommits/Keyword/<ProjectName>/prevFiles/`".
      - **Fixed version** of the HDL code file, stored in the directory "`data/PatchCommits/Keyword/<ProjectName>/revFiles/`".
      - **Diff Hunk** of the code changes of fixing the bug, stored in the directory "`data/PatchCommits/Keyword/<ProjectName>/DiffEntries/`".
  - The **third step** will further filter out the HDL code files that only contain non-HDL code changes (e.g. comments).
  - The **fourth step** perform the code clone detection based on SourcecerCC. The results will be stored in the directory "`data/CloneData/`".