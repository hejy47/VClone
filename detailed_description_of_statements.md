# The detailed description about statements in HDLs

The nodes in statement level are collected obtained [hdlConvertorAST](https://github.com/Nic30/hdlConvertorAst). In particular, `HdlIdDef` involves declaration of variables (e.g. port, parm), which is one of the types of statements considered in this study. Therefore, we considered the following 16 types of statements in this experiment.

1. `HdlIdDef`: Declaration of port, parameter, type etc.
2. `HdlStmNop`: Nop statement
3. `HdlStmBlock`: The body block of statements in HDL (i.e., begin/end block). 
4. `HdlStmAssign`: Assignment statement
5. `HdlStmIf`: If statement
6. `HdlStmProcess`: Process statement
7. `HdlStmCase`: Case statement
8. `HdlStmFor`: For statement
   ```
   for (init, cond, step)
      body
   ```
9. `HdlStmForIn`: For in statement
   ```
   for var in collection:
      body
   ```
10.  `HdlStmWhile`: While statement
      ```
      while cond:
         body
      ```
11. `HdlStmRepeat`: Repeat statement
12. `HdlStmReturn`: Return statement
13. `HdlStmWait`: Wait statement
14. `HdlStmBreak`: Break statement
15. `HdlStmContinue`: Continue statement
16. `HdlStmThrow`: Throw (raise) statement
