# PATCH-CLR35
Provide CLR3.5 compliant patches for higher versions of VS (2008).

### WHY
the compiled on anything higher than VS2008 defaults to `CLR v4`,
and even if `.net framework 3.5` is selected, 
it will not run in Windows 7 without `.net framework 4` installed.

### 
maintain compatibility with `.net framework 3.5` at development time, 
replacing the `metadata.version` field in the program (unrecommended)
will allow use in `.net framework 3.5` environments.