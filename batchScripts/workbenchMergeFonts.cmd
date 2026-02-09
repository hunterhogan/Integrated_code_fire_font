@ECHO OFF

py -m Integrated_Code_Fire.mergeFonts

@PUSHD %pathWorkbenchFonts%

DEL FiraCode*.ttf
DEL SourceHanMonoSC*.otf

@POPD

py -m Integrated_Code_Fire.writeMetadata
