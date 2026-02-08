@ECHO OFF

SET pathDestination="%pathRoot%\fonts"
SET filenameMask=I*.ttf
ROBOCOPY %pathWorkbenchFonts% %pathDestination% %filenameMask% /MOV /NS /NC /NDL /NJH /NJS /unicode

SET filename=IntegratedCode.zip

PUSHD %pathDestination%
7z a "%filename%" "%filenameMask%" -mx=9
POPD
