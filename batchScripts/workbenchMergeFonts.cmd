@ECHO OFF

SET pathSource="%pathRoot%\Fira_Code_v6.99\ttf\Fira Code"
SET filenameMask=*.ttf
ROBOCOPY %pathSource% %pathWorkbenchFonts% %filenameMask% /NS /NC /NDL /NJH /NJS

py -m Integrated_Code_Fire.mergeFonts


@PUSHD %pathWorkbenchFonts%

DEL FiraCode*.ttf
DEL SourceHanMonoSC*-scaled.ttf

@POPD


py -m Integrated_Code_Fire.writeMetadata
