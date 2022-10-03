import os
import re
from hdlConvertorAst.language import Language
from hdlConvertorAst.hdlAst import ALL_STATEMENT_CLASSES, HdlIdDef, HdlCompInst
# from hdlConvertorAst.hdlAst import HdlStmBlock, HdlStmProcess, HdlFunctionDef
from hdlConvertor import HdlConvertor

def getBlocks(filestring, logging, filePath):
    global positions
    filenames = [filePath]
    includeDirs = [os.path.dirname(filePath)]
    c = HdlConvertor()
    filestring2 = c.verilog_pp(filePath, Language.VERILOG, includeDirs)
    vAst = None
    try:
        vAst = c.parse(filenames, Language.VERILOG, includeDirs,
                       hierarchyOnly=False, debug=True)
    except Exception as e:
        logging.warning("File " + filePath + " cannot be parsed. " + str(e))
        return (None, None)

    linecount = filestring.count("\n")
    if not filestring.endswith("\n"):
        linecount += 1

    statement_linenos = []
    statement_types = []
    block_linenos = []
    strings = []
    delta_lines = 5

    children = []
    children.extend(vAst.objs)
    for index, obj in enumerate(children):
        if type(obj) in ALL_STATEMENT_CLASSES or type(obj) == HdlIdDef:
            blockString = "\n".join(filestring2.splitlines()[obj.position.start_line-1:obj.position.stop_line])
            if blockString != "" and blockString in filestring and blockString not in strings:
                start_lineno = filestring[:filestring.index(blockString)].count("\n") + 1
                end_lineno = start_lineno + obj.position.stop_line - obj.position.start_line
                statement_types.append(obj.__class__.__name__)
                statement_linenos.append((start_lineno, end_lineno))
                start_lineno = start_lineno - delta_lines if start_lineno -delta_lines > 0 else 0
                end_lineno = end_lineno + delta_lines if end_lineno + delta_lines < linecount else linecount
                blockString = "\n".join(filestring.splitlines()[start_lineno-1:end_lineno])
                block_linenos.append((start_lineno, end_lineno))
                strings.append(blockString)
        if hasattr(obj, "objs"):
            children.extend(obj.objs)
    
    return (statement_types, statement_linenos, block_linenos, strings)
		

if __name__ == "__main__":
    aPath = "/mnt/APR4V/HDLClone/subjects/darkriscv/rtl/darkriscv.v"
    aContent = open(aPath, 'r').read()
    a1 = getBlocks(aContent, None, aPath)
    print(a1)