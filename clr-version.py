#!/usr/bin/env python3
# -*- coding=utf-8 -*-


''' https://github.com/construct/construct '''
from construct import *
from construct.lib import *
from construct.core import *


''' https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/System/Diagnostics/Debug/struct.IMAGE_COR20_HEADER.html '''
IMAGE_DATA_DIRECTORY = Struct(
    "VirtualAddress" / Int32ul,
    "Size" / Int32ul,
)
IMAGE_COR20_HEADER_0 = Union(None,
    "EntryPointToken" / Int32ul,
    "EntryPointRVA" / Int32ul,
)
IMAGE_COR20_HEADER = Struct(
    "cb" / Int32ul,
    "MajorRuntimeVersion" / Int16ul,
    "MinorRuntimeVersion" / Int16ul,
    "MetaData" / IMAGE_DATA_DIRECTORY,
    "Flags" / Int32ul,
    "Anonymous" / IMAGE_COR20_HEADER_0,
    "Resources" / IMAGE_DATA_DIRECTORY,
    "StrongNameSignature" / IMAGE_DATA_DIRECTORY,
    "CodeManagerTable" / IMAGE_DATA_DIRECTORY,
    "VTableFixups" / IMAGE_DATA_DIRECTORY,
    "ExportAddressTableJumps" / IMAGE_DATA_DIRECTORY,
    "ManagedNativeHeader" / IMAGE_DATA_DIRECTORY,
)
''' https://github.com/dotnet/runtime/blob/main/src/coreclr/inc/mdfileformat.h '''
STORAGESIGNATURE = Struct(
    "lSignature" / Int32ul,  # COR20MetadataSignature
    Check(this.lSignature == 0x424a5342),
    "iMajorVer" / Int16ul,
    "iMinorVer" / Int16ul,
    "iExtraData" / Int32ul,
    "iVersionString" / Int32ul,
    "pVersion" / CString("utf8"),
)


''' https://github.com/lief-project/LIEF '''
import lief

import sys, pathlib


if (len(sys.argv) < 2):
    print( f'usage: clr-version <dotnet program>' ); exit(0)

library = lief.PE.parse(sys.argv[1])


HasCorHeader = lambda : \
    library.data_directory(lief.PE.DATA_DIRECTORY.CLR_RUNTIME_HEADER).has_section

GetCorHeader = lambda : \
    library.get_content_from_virtual_address(
        library.data_directory(lief.PE.DATA_DIRECTORY.CLR_RUNTIME_HEADER).rva,
        library.data_directory(lief.PE.DATA_DIRECTORY.CLR_RUNTIME_HEADER).size)

GetMetadata = lambda MetaData: \
    library.get_content_from_virtual_address(
        MetaData.VirtualAddress,
        MetaData.Size)


if (not HasCorHeader()):
    print( 'non-dotnet program' ); exit(0)

corHeader = IMAGE_COR20_HEADER.parse(GetCorHeader())

metadata = STORAGESIGNATURE.parse(GetMetadata(corHeader.MetaData))

'''
CLR2-3: 'v2.0.50727'
CLR4: 'v4.0.30319'
'''
print( f'clr version: {metadata.pVersion}' )


'''
the compiled on anything higher than VS2008 defaults to `CLR v4`,
and even if `.net framework 3.5` is selected, 
it will not run in Windows 7 without `.net framework 4` installed.


maintain compatibility with `.net framework 3.5` at development time, 
replacing the `metadata.version` field in the program (unrecommended)
will allow use in `.net framework 3.5` environments.


https://learn.microsoft.com/troubleshoot/developer/dotnet/framework/general/sgen-mixed-mode-assembly-built-v2-0-50727
'''